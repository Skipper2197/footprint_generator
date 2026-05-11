from src.generator import extract_footprint, export_gdf
from src.viz import plot_validation
import os
import sys
from pathlib import Path
import PySide6
import matplotlib.pyplot as plt

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

        self.current_folder = None
        self.last_gdf = None

        # creates the main UI components
        self.display = FigureDisplayArea()
        self.controls = ControlPanel(title="File Processing")
        
        # user selects a folder of TIF files to process
        self.folder_picker = FolderPicker("Source Folder:")
        
        # user selects a TIF file from the folder (empty by default)
        self.file_selector = LabeledComboBox("Select TIFF:", [])

        # export format selector
        # these file formats are relevant files for GIS creation and analysis
        self.format_selector = LabeledComboBox("Export Format:", ["GeoJSON", "GeoPackage", "Shapefile", "PNG (Image)"])
        self.controls.add_widget(self.format_selector)
        
        self.action_buttons = ButtonRow(["Generate Footprint", "Process All", "Export"])

        # coordinate reference system (CRS) dropdown menu
        # this list is designed to be malleable.
        # the user may add or remove any CRS here by filling in the relevant info.
        self.crs_options = {
            "Web Mercator (EPSG:3857)": 3857,
            "NAD83 (EPSG:4269)": 4269,
            "WGS 84 (EPSG:4326)": 4326
        }

        # UI component
        # uses the dict keys for the dropdown items
        self.crs_selector = LabeledComboBox("Target CRS:", list(self.crs_options.keys()))

        self.controls.add_widget(self.crs_selector)
        self.controls.add_widget(self.folder_picker)
        self.controls.add_widget(self.file_selector)
        self.controls.add_widget(self.action_buttons)
        
        self.main_layout = WindowWithFigureAbove(self.display, self.controls)
        self.setCentralWidget(self.main_layout)

        # cConnect folder picker to the scan function
        self.folder_picker.folder_changed.connect(self._update_file_list)

        self.action_buttons.buttons["Generate Footprint"].clicked.connect(self._process_file)
        self.action_buttons.buttons["Export"].clicked.connect(self._export_data)
        self.action_buttons.buttons["Process All"].clicked.connect(self._process_all_files)

    def _update_file_list(self, folder_path: str) -> None:
        '''
        Scans the selected folder and populates the dropdown.
        '''

        self.current_folder = folder_path  # saves the path for later use
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

        # run extraction
        self.last_gdf = extract_footprint(tif_path)

        # prepare the figure for display
        fig = self.display.get_mpl_figure()
        fig.clear()
        ax = fig.add_subplot(111)

        with rasterio.open(tif_path) as src:
            # Creates a downsampled preview for speed
            preview = src.read(1, out_shape=(src.height // 10, src.width // 10))
            
            # Use plotting_extent to get [xmin, xmax, ymin, ymax] in map coordinates
            extent = plotting_extent(src)
            
            # Show the raster preview
            ax.imshow(preview, extent=extent, cmap='viridis')
            
            # Overlay the footprint
            if not self.last_gdf.empty:
                self.last_gdf.plot(ax=ax, facecolor='#ff7f0e', alpha=0.3, edgecolor='#ff7f0e', linewidth=2)
            
            ax.set_title(f"Footprint for {filename}")

        # Refresh the canvas
        self.display.mpl_canvas.draw()
        return None
    
    def _export_data(self) -> None:
        if not hasattr(self, 'last_gdf') or self.last_gdf is None:
            print("No data to export. Try 'Generate Footprint' first.")
            return

        # import CRS dictionary
        selected_crs_name = self.crs_selector.combo.currentText()
        target_epsg = self.crs_options[selected_crs_name]

        filename = self.file_selector.combo.currentText()
        base_name = os.path.splitext(filename)[0]
        fmt = self.format_selector.combo.currentText()
        
        # Ensure export directory exists
        os.makedirs('./exports', exist_ok=True)

        if fmt == "PNG (Image)":
            out_path = os.path.join('./exports', f"{base_name}.png")
            self._save_png_preview(out_path)
        else:
            ext_map = {"GeoJSON": ".geojson", "GeoPackage": ".gpkg", "Shapefile": ".shp"}
            driver_map = {"GeoJSON": "GeoJSON", "GeoPackage": "GPKG", "Shapefile": "ESRI Shapefile"}
            
            out_path = os.path.join('./exports', f"{base_name}{ext_map[fmt]}")
            export_gdf(self.last_gdf, out_path, driver=driver_map[fmt], epsg=target_epsg)

    def _save_png_preview(self, path: str) -> None:
        filename = self.file_selector.combo.currentText()
        tif_path = os.path.join(self.current_folder, filename)

        # Create a "headless" figure
        fig, ax = plt.subplots(figsize=(10, 10))

        try:
            with rasterio.open(tif_path) as src:
                # Create a downsampled preview for the background (1/10th scale)
                preview = src.read(1, out_shape=(src.height // 10, src.width // 10))
                
                # Map the pixel coordinates to geographic coordinates
                extent = plotting_extent(src)
                
                # Draw the raster background
                ax.imshow(preview, extent=extent, cmap='viridis')
                
                # Overlay the footprint on top
                self.last_gdf.plot(ax=ax, facecolor='#ff7f0e', alpha=0.3, edgecolor='#ff7f0e', linewidth=2)
                
                ax.set_title(f"Boundary Overlay: {filename}")
                ax.set_axis_off()  # Keeps the focus on the data, not the plot axes
                
                # Save with high resolution
                fig.savefig(path, bbox_inches='tight', dpi=300)
                print(f"Saved overlay image to {path}")

        except Exception as e:
            print(f"Failed to generate PNG overlay: {e}")
        
        plt.close(fig)

    def _process_all_files(self) -> None:
        if not self.current_folder:
            print("Please select a source folder first.")
            return

        # Get list of all TIFF files
        files = [f for f in os.listdir(self.current_folder) if f.lower().endswith(('.tif', '.tiff'))]
        
        selected_fmt = self.format_selector.combo.currentText()
        print(f"Starting batch process for {len(files)} files into {selected_fmt} format...")

        for filename in files:
            try:
                tif_path = os.path.join(self.current_folder, filename)
                
                # Extract the footprint using your generator logic
                gdf = extract_footprint(tif_path)

                if not gdf.empty:
                    # Use the generalized export logic
                    # We temporarily set self.last_gdf so we can reuse the _export_data logic
                    self.last_gdf = gdf
                    
                    # Update the combo box selection so the export naming is correct
                    index = self.file_selector.combo.findText(filename)
                    if index >= 0:
                        self.file_selector.combo.setCurrentIndex(index)
                    
                    self._export_data()

            except Exception as e:
                print(f"Failed to process {filename}: {e}")

        print(f"Batch processing complete. All files exported to {selected_fmt}.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GeoJsonGeneratorApp()
    window.show()
    sys.exit(app.exec())
