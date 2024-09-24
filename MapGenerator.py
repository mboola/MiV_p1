import pandas as pd
import geopandas as gpd
from shapely import wkt
import plotly.graph_objects as go

# Load the CSV file
comarques = pd.read_csv("comarques_catalunya.csv")
municipis = pd.read_csv("municipis_catalunya.csv")

# Convert the 'Georeferència' column (which is WKT) to actual geometries
comarques['geometry'] = comarques['Georeferència'].apply(wkt.loads)

# Read the additional CSV file that contains 'municipi' and 'total'
municipis_habitants = pd.read_csv("habitants_municipis.csv")

municipis_habitants_2020 = municipis_habitants[municipis_habitants['Any'] == 2020].copy()

municipis_habitants_2020['Total 0-4'] = pd.to_numeric(municipis_habitants_2020['Total 0-4'], errors='coerce')
municipis_habitants_2020['Total 15-64'] = pd.to_numeric(municipis_habitants_2020['Total 15-64'], errors='coerce')
municipis_habitants_2020['Total 65+'] = pd.to_numeric(municipis_habitants_2020['Total 65+'], errors='coerce')

# Create the 'total' column by summing the specified fields
municipis_habitants_2020.loc[:, 'Total'] = (
    municipis_habitants_2020['Total 0-4'] +
    municipis_habitants_2020['Total 15-64'] +
    municipis_habitants_2020['Total 65+']
)

comarques['Total'] = 0

# Iterate through municipis_habitants_2020 to update comarques
for index, row in municipis_habitants_2020.iterrows():
    municipi = row['Municipi']              # Get municipi
    total_habitants_municipi = row['Total'] # Get total

    # Find the row in municipis with NOMMUNI = municipi
    municipi_row = municipis[municipis['NOMMUNI'] == municipi]
    
    if not municipi_row.empty:
        comarca = municipi_row['NOMCOMAR'].values[0]  # Get the value of NOMCOMAR

        # Find the row in comarques where NOMCOMAR matches
        comarca_row = comarques[comarques['NOMCOMAR'] == comarca]
        
        if not comarca_row.empty:
            # Update the 'Total' field in comarques
            comarques.loc[comarques['NOMCOMAR'] == comarca, 'Total'] += total_habitants_municipi

# Print the updated comarques DataFrame
print(comarques)



# Convert merged DataFrame to GeoDataFrame
gdf = gpd.GeoDataFrame(comarques, geometry='geometry')

# Convert GeoDataFrame to GeoJSON format
geojson_data = gdf.__geo_interface__

# Create a Plotly figure
fig = go.Figure()

# Add the GeoJSON data to the figure
fig.add_trace(go.Choroplethmapbox(
    geojson=geojson_data,
    locations=gdf.index,
    z=gdf['Total'], #[1]*len(gdf),
    colorscale="Viridis",  # You can choose other color scales
    marker_line_width=1,  # Width of the borders
    marker_line_color='black',  # Color of the borders
    text=gdf['NOMCOMAR'],  # Tooltip text
    hoverinfo='text',
))

# Set the layout
fig.update_layout(
    mapbox_style="white-bg",  # Set to a white background
    mapbox_zoom=7,  # Decrease zoom level (originally was 8)
    mapbox_center={"lat": 41.6940, "lon": 2.0290},  # Center of Barcelona
    margin={"r": 10, "t": 10, "l": 10, "b": 10},  # Remove margins
    shapes=[  # Adding a black rectangle
        dict(
            type="rect",
            xref="paper", yref="paper",
            x0=1, y0=1,
            x1=1, y1=1,
            opacity=0,
            line=dict(color="black", width=1),
        )
    ]
)

# Show the figure
fig.show()
