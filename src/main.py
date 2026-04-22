from generator import extract_footprint, save_geojson
from viz import plot_validation
import os

SOURCE_DIR = './data/example_data/'

def main():
    for tif_file in os.listdir(SOURCE_DIR):
        tif_path = f'{SOURCE_DIR}/{tif_file}'
        gdf = extract_footprint(tif_path)

        # plot_validation(tif_path, gdf)

        save_geojson(gdf, f'geojsons/{os.path.splitext(tif_file)[0]}.geojson')
    return

if __name__ == '__main__':
    main()
