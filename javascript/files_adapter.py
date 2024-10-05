import pandas as pd
import geopandas as gpd
from shapely.wkt import loads

def convert_to_geojson(df, geojson_file):
    # Create a GeoDataFrame
    gdf = gpd.GeoDataFrame(df)

    # Convert the WKT geo to shapely geometries
    gdf['geo'] = gdf['geo'].apply(loads)

    # Set the GeoDataFrame's geo
    gdf = gdf.set_geometry('geo')

    # Save to GeoJSON file
    gdf.to_file(geojson_file, driver='GeoJSON')

convert_to_geojson(pd.read_csv('base_files/comarques.csv', usecols=['NOMCOMAR', 'geo']), 'geojson_files/comarques.geojson')
convert_to_geojson(pd.read_csv('base_files/municipis.csv', usecols=['geo', 'NOMMUNI', 'NOMCOMAR']), 'geojson_files/municipis.geojson')
