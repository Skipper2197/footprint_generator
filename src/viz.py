import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt

def plot_validation(tif_path: str, footprint_gdf) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    with rasterio.open(tif_path) as src:
        ax1.set_title("BEFORE: Raw Raster (TIFF)")
        preview = src.read(1, out_shape=(src.height // 10, src.width // 10))
        show(preview, ax=ax1, cmap='viridis')

        ax2.set_title("AFTER: Accurate Tilted Footprint")
        # Get the boundary of the geometry

        footprint_gdf.plot(ax=ax2, facecolor='#ff7f0e', alpha=0.3, edgecolor='#ff7f0e', linewidth=2)

        ax2.set_aspect('equal') # Prevent the shape from warping when resizing window

    plt.tight_layout()
    plt.show()
