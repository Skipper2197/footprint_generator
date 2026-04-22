from src.generator import extract_footprint, save_geojson
from src.viz import plot_validation
import os
import sys
from pathlib import Path
import PySide6

# This automatically finds the plugins folder relative to the user's PySide6 install
pyside_root = Path(PySide6.__file__).parent
plugin_path = str(pyside_root / "plugins")
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(pyside_root / "plugins" / "platforms")
os.environ["QT_API"] = "pyside6"

from PySide6.QtWidgets import QApplication, QMainWindow
from src.pysidecomp import (
    FigureDisplayArea, ControlPanel, LabeledInput, 
    LabeledSlider, ButtonRow, WindowWithFigureAbove,
    LabeledComboBox, FolderPicker
)
from src.generator import extract_footprint #
import rasterio
from rasterio.plot import plotting_extent

class GeoJsonGeneratorApp(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Satellite Footprint Generator")
        self.resize(1000, 700)

        # 1. Create UI Components
        self.display = FigureDisplayArea()
        self.controls = ControlPanel(title="File Processing")
        
        # 1. NEW: The Folder Picker
        self.folder_picker = FolderPicker("Source Folder:")
        
        # 2. The File Selector (Starts empty now)
        self.file_selector = LabeledComboBox("Select TIFF:", [])
        
        self.action_buttons = ButtonRow(["Generate Footprint", "Process All", "Export GeoJSON"])

        # Add to layout
        self.controls.add_widget(self.folder_picker)
        self.controls.add_widget(self.file_selector)
        self.controls.add_widget(self.action_buttons)
        
        self.main_layout = WindowWithFigureAbove(self.display, self.controls)
        self.setCentralWidget(self.main_layout)

        # 3. Signals: Connect folder picker to the scan function
        self.folder_picker.folder_changed.connect(self._update_file_list)

        self.action_buttons.buttons["Generate Footprint"].clicked.connect(self._process_file)
        self.action_buttons.buttons["Export GeoJSON"].clicked.connect(self._export_geojson)
        self.action_buttons.buttons["Process All"].clicked.connect(self._process_all_files)

    def _update_file_list(self, folder_path: str) -> None:
        '''
        Scans the selected folder and populates the dropdown.
        '''

        self.current_folder = folder_path  # Save the path for later use
        self.file_selector.combo.clear()
        files = [f for f in os.listdir(folder_path)]
        
        if files:
            self.file_selector.combo.addItems(files)
            print(f"Found {len(files)} TIFF files.")
        else:
            print("No TIFF files found in this directory.")

    def _process_file(self) -> None:
        filename = self.file_selector.combo.currentText()
        if not filename or not self.current_folder:
            return 

        tif_path = os.path.join(self.current_folder, filename)

        # 1. Run extraction
        self.last_gdf = extract_footprint(tif_path)

        # 2. Prepare the figure
        fig = self.display.get_mpl_figure()
        fig.clear()
        ax = fig.add_subplot(111)

        with rasterio.open(tif_path) as src:
            # Create a downsampled preview for speed
            # (Matches the scale_factor=10 in your generator)
            preview = src.read(1, out_shape=(src.height // 10, src.width // 10))
            
            # Use plotting_extent to get [xmin, xmax, ymin, ymax] in map coordinates
            extent = plotting_extent(src)
            
            # Show the raster preview
            ax.imshow(preview, extent=extent, cmap='viridis')
            
            # 3. Overlay the footprint
            if not self.last_gdf.empty:
                self.last_gdf.plot(ax=ax, facecolor='#ff7f0e', alpha=0.3, edgecolor='#ff7f0e', linewidth=2)
            
            ax.set_title(f"Footprint for {filename}")

        # 4. Refresh the canvas
        self.display.mpl_canvas.draw()
        return None
    
    def _export_geojson(self) -> None:
        # Ensure you have a GDF to save
        if not hasattr(self, 'last_gdf') or self.last_gdf is None:
            print("Generate a footprint first!")
            return
            
        filename = self.file_selector.combo.currentText()
        out_path = os.path.join('./geojsons', f"{os.path.splitext(filename)[0]}.geojson")
        
        save_geojson(self.last_gdf, out_path)

    def _process_all_files(self) -> None:
        if not self.current_folder:
            print("Please select a source folder first.")
            return

        # 1. Get list of all TIFF files
        files = [f for f in os.listdir(self.current_folder) if f.lower().endswith(('.tif', '.tiff'))]
        
        if not files:
            print("No TIFF files found to process.")
            return
        
        print(f"Starting process for {len(files)} files...")

        for filename in files:
            try:
                tif_path = os.path.join(self.current_folder, filename)
                
                # Extract the footprint
                gdf = extract_footprint(tif_path)

                if not gdf.empty:
                        # Save automatically to the root geojsons folder
                        out_name = f"{os.path.splitext(filename)[0]}.geojson"
                        out_path = os.path.join('./geojsons', out_name)
                        save_geojson(gdf, out_path)
                        print(f"Processed: {filename}")
                
            except Exception as e:
                print(f"Failed to process {filename}: {e}")
        print("Processing complete.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GeoJsonGeneratorApp()
    window.show()
    sys.exit(app.exec())
