import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import os

def plot_validation(tif_path: str, footprint_gdf) -> None:
    with rasterio.open(tif_path) as src:
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Plot the actual image (RGB or Single Band)
        show(src, ax=ax, cmap='pink') 
        
        # Overlay the extracted footprint as a bright outline
        footprint_gdf.plot(ax=ax, facecolor='none', edgecolor='yellow', linewidth=2)
        
        ax.set_title(f"Validation: {os.path.basename(tif_path)}")
        plt.show()