from generator import extract_footprint, save_geojson
from viz import plot_validation

TIF_FILE = 'data/example_data/LC09_L2SP_015034_20260228_20260301_02_T1_ST_DRAD.TIF'

def main():
    gdf = extract_footprint(TIF_FILE)

    plot_validation(TIF_FILE, gdf)

    save_geojson(gdf, 'geojsons/test.geojson')
    return

if __name__ == '__main__':
    main()