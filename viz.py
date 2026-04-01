import rasterio
import numpy as np # Add this
from rasterio.plot import show
from rasterio.features import shapes
from shapely.geometry import shape
import matplotlib.pyplot as plt

# tif_path = "data/LC09_L2SP_015034_20260228_20260301_02_T1_SR_B1.TIF"
# tif_path = "data/LC09_L2SP_015034_20260228_20260301_02_T1_SR_B7.TIF"
tif_path = "data/LC09_L2SP_015034_20260228_20260301_02_T1_ST_DRAD.TIF"

with rasterio.open(tif_path) as src:
    # Read the actual data using a small sample for speed (out_shape)
    img = src.read(1, out_shape=(src.height // 10, src.width // 10))
    
    # 1. Create a mask based on actual pixel values
    # No data = 0, convert to int for results below
    mask = (img > 0).astype(np.uint8) 
    
    # 2. Extract shapes from this  mask
    results = (
        {'geometry': s} 
        for s, v in shapes(mask) 
        if v == 1 
    )
    
    # 3. Get the first valid polygon
    footprint_geom = shape(next(results)['geometry'])

# Setup the Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

ax1.set_title("BEFORE: Raw Raster (TIFF)")
show(img, ax=ax1, cmap='viridis')

ax2.set_title("AFTER: Accurate Tilted Footprint")
# Get the boundary of the geometry
x, y = footprint_geom.exterior.xy
ax2.plot(x, y, color='#ff7f0e', linewidth=2)
ax2.fill(x, y, color='#ff7f0e', alpha=0.3)
ax2.invert_yaxis() # Match the raster orientation, image data has zero at top
ax2.set_aspect('equal') # Prevent the shape from warping when resizing window

plt.tight_layout()
plt.show()