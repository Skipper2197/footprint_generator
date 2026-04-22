from generator import extract_footprint, save_geojson
from viz import plot_validation
import os

SOURCE_DIR = './data/example_data/'

def main():
    for tif_file in os.listdir(SOURCE_DIR):
        tif_path = f'{SOURCE_DIR}/{tif_file}'
        gdf = extract_footprint(tif_path)

        # plot_validation(tif_path, gdf)
        epsg = int(input("What projected coordinate system do you want to use? The default is NAD83: 4326, but NATRF2022: 10966 is the most recently updated CRS"))
        save_geojson(gdf, f'geojsons/{os.path.splitext(tif_file)[0]}.geojson', epsg)
    return

if __name__ == '__main__':
    main()
