import pandas as pd
import geopandas as gpd
from shapely.wkt import loads
import re

comarques_df = pd.read_csv('base_files/comarques.csv', usecols=['geo', 'NOMCOMAR'])
municipis_df = pd.read_csv('base_files/municipis.csv', usecols=['geo', 'NOMMUNI', 'NOMCOMAR'])

# Create a list of Municipis for each comarca
municipis_grouped = municipis_df.groupby('NOMCOMAR')['NOMMUNI'].apply(list).reset_index()
comarques_df = pd.merge(comarques_df, municipis_grouped, on='NOMCOMAR', how='left')

poblacio_municipis_df = pd.read_csv('base_files/habitants_municipis.csv', usecols=['Municipi', 'Total 0-14', 'Total 15-64', 'Total 65+', 'Any'])

def normalize_region_name(name):
    name = name.lower()

    name = name.strip()
    
    # Remove punctuation except for apostrophes in certain cases
    name = re.sub(r"[,.]", "", name)  # Remove commas and periods
    # Handle apostrophes correctly
    name = re.sub(r"\bl'", "l ", name)  # Change "l'" to "l" with a space for sorting

    # Sort words (if necessary) and remove extra spaces
    words = name.split()
    words.sort()  # Sort alphabetically
    normalized_name = ' '.join(words)
    
    return normalized_name

def adapt_names(df):
    print

poblacio_municipis_df.loc[:, 'Municipi'] = poblacio_municipis_df['Municipi'].apply(normalize_region_name)
municipis_df.loc[:, 'NOMMUNI'] = municipis_df['NOMMUNI'].apply(normalize_region_name)

adapt_names(poblacio_municipis_df)

# TODO : use all, not only year 2020
poblacio_municipis_df = poblacio_municipis_df[poblacio_municipis_df['Any'] == 2020]

poblacio_municipis_df['Total'] = poblacio_municipis_df['Total 0-14'] + poblacio_municipis_df['Total 15-64'] + poblacio_municipis_df['Total 65+']

# TODO : separate in years
comarques_df['Total'] = 0

for _, row in poblacio_municipis_df.iterrows():
    municipi = row['Municipi']
    total_habitants_municipi = row['Total']
    
    municipi_row = municipis_df[municipis_df['NOMMUNI'] == municipi]
    if not municipi_row.empty:
        municipis_df.loc[municipis_df['NOMMUNI'] == municipi, 'Total'] = total_habitants_municipi
        
        comarca = municipi_row['NOMCOMAR'].values[0]
        comarca_row = comarques_df[comarques_df['NOMCOMAR'] == comarca]

        if not comarca_row.empty:
            comarques_df.loc[comarques_df['NOMCOMAR'] == comarca, 'Total'] += total_habitants_municipi
        else:
            print("Comarca not found: " + comarca + " inside comarques_df")
    else:
        print("Municipi not found: " + municipi + " inside municipis_df")


def convert_to_geojson(df, geojson_file):
    # Create a GeoDataFrame
    gdf = gpd.GeoDataFrame(df)

    # Convert the WKT geo to shapely geometries
    gdf['geo'] = gdf['geo'].apply(loads)

    # Set the GeoDataFrame's geo
    gdf = gdf.set_geometry('geo')

    # Save to GeoJSON file
    gdf.to_file(geojson_file, driver='GeoJSON')


convert_to_geojson(comarques_df, 'geojson_files/comarques.geojson')
convert_to_geojson(municipis_df, 'geojson_files/municipis.geojson')
