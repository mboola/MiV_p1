import pandas as pd
import geopandas as gpd
from shapely import wkt
import re
import plotly.graph_objects as go

comarques = pd.read_csv("comarques_catalunya.csv")
municipis = pd.read_csv("municipis_catalunya.csv")
habitants_municipis = pd.read_csv("habitants_municipis.csv")

habitants_municipis = habitants_municipis[habitants_municipis['Any'] == 2020]

habitants_municipis.loc[:, 'Total 0-14'] = pd.to_numeric(habitants_municipis['Total 0-14'], errors='coerce')
habitants_municipis.loc[:, 'Total 15-64'] = pd.to_numeric(habitants_municipis['Total 15-64'], errors='coerce')
habitants_municipis.loc[:, 'Total 65+'] = pd.to_numeric(habitants_municipis['Total 65+'], errors='coerce')

# Create the 'total' column by summing the specified fields
habitants_municipis.loc[:, 'Total'] = (
    habitants_municipis['Total 0-14'].fillna(0) +  # Handle NaN values
    habitants_municipis['Total 15-64'].fillna(0) +
    habitants_municipis['Total 65+'].fillna(0)
)

# Convert the 'Georeferència' column (which is WKT) to actual geometries
comarques['geometry'] = comarques['Georeferència'].apply(wkt.loads)

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


# Normalize names in both DataFrames
habitants_municipis.loc[:, 'Normalized'] = habitants_municipis['Municipi'].apply(normalize_region_name)
municipis.loc[:, 'Normalized'] = municipis['NOMMUNI'].apply(normalize_region_name)

comarques['Total'] = 0

# Iterate through habitants_municipis_2020 to update comarques
for index, row in habitants_municipis.iterrows():
    municipi = row['Normalized']              # Get municipi
    total_habitants_municipi = row['Total'] # Get total

    # Find the row in municipis with NOMMUNI = municipi
    municipi_row = municipis[municipis['Normalized'] == municipi]
    
    if not municipi_row.empty:
        comarca = municipi_row['NOMCOMAR'].values[0]  # Get the value of NOMCOMAR

        # Find the row in comarques where NOMCOMAR matches
        comarca_row = comarques[comarques['NOMCOMAR'] == comarca]
        
        if not comarca_row.empty:
            # Update the 'Total' field in comarques
            comarques.loc[comarques['NOMCOMAR'] == comarca, 'Total'] += total_habitants_municipi
        else:
            print("comarca not found: %s", comarca)


# Print the updated comarques DataFrame
# Print all comarques where Total is equal to 0
#comarques_with_zero_total = comarques[comarques['Total'] == 0]

# Check if any comarques were found
#if not comarques_with_zero_total.empty:
#    print(comarques_with_zero_total)



# Convert merged DataFrame to GeoDataFrame
gdf = gpd.GeoDataFrame(comarques, geometry='geometry')

# Convert GeoDataFrame to GeoJSON format
geojson_data = gdf.__geo_interface__

# Create a Plotly figure
fig = go.Figure()

# Customize hover text to include both region name and total population
comarques['hover_text'] = comarques.apply(
    lambda row: f"Comarca: {row['NOMCOMAR']}<br>Població total: {row['Total']:,}", axis=1
)

# Add the GeoJSON data to the figure with a color bar (legend)
fig.add_trace(go.Choroplethmapbox(
    geojson=geojson_data,
    locations=comarques.index,
    z=comarques['Total'],  # Population data
    colorscale="Viridis",  # You can choose other color scales (e.g., 'Blues', 'Greens')
    marker_line_width=1,  # Width of the borders
    marker_line_color='black',  # Color of the borders
    text=comarques['hover_text'],  # Tooltip text
    hoverinfo='text',
    colorbar=dict(
        title="Population",       # Title of the legend
        titleside="right",        # Title position
        tickvals=[500000, 1000000, 1500000, 2000000, 2500000],  # Custom ticks (adjust according to your data)
        ticktext=["500k", "1M", "1.5M", "2M", "2.5M"],  # Custom labels
        len=0.7,                 # Length of the color bar (percentage of the figure height)
    )
))

# Set the layout, including a title
fig.update_layout(
    mapbox_style="white-bg",  # Set to a white background
    mapbox_zoom=7,  # Zoom level
    mapbox_center={"lat": 41.6940, "lon": 2.0290},  # Center the map
    margin={"r": 10, "t": 10, "l": 10, "b": 10},  # Remove margins
    title={
        'text': "Population Distribution by Region in 2020",  # Add your title here
        'y': 0.95,  # Position of the title (closer to the top)
        'x': 0.5,   # Center align the title
        'xanchor': 'center',
        'yanchor': 'top',
    },
    title_font=dict(size=20),  # Customize title font size
    # Add the black rectangle shape around the map
    shapes=[
        dict(
            type="rect",
            xref="paper", yref="paper",  # Coordinate system for positioning
            x0=0, y0=0,  # Bottom left corner of the rectangle
            x1=1, y1=1,  # Top right corner of the rectangle
            line=dict(color="black", width=4),  # Black border with width 4
        )
    ]
)

# Show the figure
fig.show()
