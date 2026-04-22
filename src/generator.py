import rasterio
import numpy as np
import geopandas as gpd
from rasterio.features import shapes
from shapely.geometry import shape

def extract_footprint(tif_path: str, scale_factor:int = 10) -> gpd.GeoDataFrame:
    with rasterio.open(tif_path) as src:
        new_height = src.height // scale_factor
        new_width = src.width // scale_factor
        
        # Read the mask at lower resolution
        mask = src.read_masks(1, out_shape=(new_height, new_width))

        # Adjust the transform to match the downsampled scale
        transform = src.transform * src.transform.scale(
            (src.width / mask.shape[1]),
            (src.height / mask.shape[0])
        )

        results = (
            {'geometry': s} 
            for s, v in shapes(mask, transform=transform) 
            if v == 255
        )

        footprint_geom = shape(next(results)['geometry'])

        footprint = gpd.GeoDataFrame([{'geometry': footprint_geom}], crs=src.crs)

        return footprint
    
def save_geojson(gdf: gpd.GeoDataFrame, out_path: str, epsg: int =4326) -> None:
    gdf_out = gdf.to_crs(epsg=epsg)
    gdf_out.to_file(out_path, driver='GeoJSON')
    print(f'File saved to {out_path}')
    return