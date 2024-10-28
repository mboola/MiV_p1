import pandas as pd
import geopandas as gpd
from shapely.wkt import loads
import re

comarques_df = pd.read_csv('base_files/comarques.csv', usecols=['geo', 'NOMCOMAR'])
municipis_df = pd.read_csv('base_files/municipis.csv', usecols=['geo', 'NOMMUNI', 'NOMCOMAR', 'CODIMUNI'])

# Create a list of Municipis for each comarca
municipis_grouped = municipis_df.groupby('NOMCOMAR')['CODIMUNI'].apply(list).reset_index()
comarques_df = pd.merge(comarques_df, municipis_grouped, on='NOMCOMAR', how='left')

poblacio_municipis_df = pd.read_csv('base_files/poblation_mun.csv', usecols=['mun', 'year', 'f_pop'])

# For each year and each mun in poblacio_municipis_df, add values and create a new df with fields mun, year and total.
poblacio_municipis_total_df = (
    poblacio_municipis_df.groupby(['mun', 'year'])['f_pop']
    .sum()
    .reset_index()
    .rename(columns={'f_pop': 'Total'})  # Rename 'f_pop' to 'total' for clarity
)

totals_by_mun = (
    poblacio_municipis_total_df.pivot(index='mun', columns='year', values='Total')
    .apply(lambda row: row.dropna().to_dict(), axis=1)
    .reset_index()
    .rename(columns={0: 'Total'})
)

municipis_df = municipis_df.merge(totals_by_mun, left_on='CODIMUNI', right_on='mun', how='left')
municipis_df = municipis_df.drop(columns=['mun'])

#print("Columns in municipis_df:", municipis_df.columns)
#print(municipis_df)

comarques_df['Total'] = [{} for _ in range(len(comarques_df))]

for _, row in municipis_df.iterrows():
    municipi = row['CODIMUNI']
    comarca = row['NOMCOMAR']
    total = row['Total']
    
    #print(municipi)
    #print(total)

    comarca_row = comarques_df[comarques_df['NOMCOMAR'] == comarca]

    if not comarca_row.empty:
        comarca_index = comarca_row.index[0]

        if not comarques_df.at[comarca_index, 'Total']:
            comarques_df.at[comarca_index, 'Total'] = {}

        # Update the Total for each year from the municipality total
        for year, population in total.items():
            if year not in comarques_df.at[comarca_index, 'Total']:
                comarques_df.at[comarca_index, 'Total'][year] = 0  # Initialize if not present
            comarques_df.at[comarca_index, 'Total'][year] += population  # Add the population
    else:
        print("Comarca not found: " + comarca + " inside comarques_df")

#print(comarques_df)

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
