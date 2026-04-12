import rasterio
import numpy as np
import geopandas as gpd
from rasterio.features import shapes
from shapely.geometry import shape

def extract_footprint(tif_path: str) -> gpd.GeoDataFrame:
    with rasterio.open(tif_path) as src:
        img = src.read(1)
        mask = (img > 0).astype(np.uint8)

        results = (
            {'geometry': s} 
            for s, v in shapes(mask, transform=src.transform) 
            if v == 1 
        )

        footprint_geom = shape(next(results)['geometry'])

        footprint = gpd.GeoDataFrame([{'geometry': footprint_geom}], crs=src.crs)

        return footprint
    
def save_geojson(gdf: gpd.GeoDataFrame, out_path: str, epsg: int =4326) -> None:
    gdf_out = gdf.to_crs(epsg=epsg)
    gdf_out.to_file(out_path, driver='GeoJSON')
    print(f'File saved to {out_path}')
    return