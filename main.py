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
    LabeledSlider, ButtonRow, WindowWithFigureAbove, LabeledComboBox
)
from src.generator import extract_footprint #
import rasterio #

SOURCE_DIR = './data/example_data/'

class GeoJsonGeneratorApp(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Satellite Footprint Generator")
        self.resize(1000, 700)

        # 1. Create UI Components
        self.display = FigureDisplayArea()
        self.controls = ControlPanel(title="File Processing")
        
        # Get list of TIFFs for the dropdown
        tiff_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.tif')]
        self.file_selector = LabeledComboBox("Select TIFF:", tiff_files)
        
        self.action_buttons = ButtonRow(["Generate Footprint", "Export GeoJSON"])

        # 2. Layout
        self.controls.add_widget(self.file_selector)
        self.controls.add_widget(self.action_buttons)
        
        self.main_layout = WindowWithFigureAbove(self.display, self.controls)
        self.setCentralWidget(self.main_layout)

        # 3. Signals
        self.action_buttons.buttons["Generate Footprint"].clicked.connect(self._process_file)
        return None

    def _process_file(self) -> None:
        filename = self.file_selector.combo.currentText()
        tif_path = os.path.join(SOURCE_DIR, filename)

        # Run your extraction logic
        gdf = extract_footprint(tif_path)

        # Plot into the GUI instead of a popup
        fig = self.display.get_mpl_figure()
        fig.clear()
        
        ax = fig.add_subplot(111)
        with rasterio.open(tif_path) as src:
            # Show a preview of the raster
            preview = src.read(1, out_shape=(src.height // 10, src.width // 10))
            ax.imshow(preview, extent=rasterio.plot.utils.get_vis_extent(src))
            
            # Overlay the footprint
            gdf.plot(ax=ax, facecolor='#ff7f0e', alpha=0.3, edgecolor='#ff7f0e', linewidth=2)
            ax.set_title(f"Footprint for {filename}")

        self.display.mpl_canvas.draw()
        return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GeoJsonGeneratorApp()
    window.show()
    sys.exit(app.exec())
