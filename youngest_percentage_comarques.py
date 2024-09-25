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

municipis_habitants_2020['Total 0-14'] = pd.to_numeric(municipis_habitants_2020['Total 0-14'], errors='coerce')
municipis_habitants_2020['Total 15-64'] = pd.to_numeric(municipis_habitants_2020['Total 15-64'], errors='coerce')
municipis_habitants_2020['Total 65+'] = pd.to_numeric(municipis_habitants_2020['Total 65+'], errors='coerce')

# Create the 'total' column by summing the specified fields
municipis_habitants_2020.loc[:, 'Total'] = (
    municipis_habitants_2020['Total 0-14'] +
    municipis_habitants_2020['Total 15-64'] +
    municipis_habitants_2020['Total 65+']
)

comarques['Total'] = 0
comarques['Total 0-14'] = 0

# Iterate through municipis_habitants_2020 toTotal update comarques
for index, row in municipis_habitants_2020.iterrows():
    municipi = row['Municipi']              # Get municipi
    total_habitants_municipi = row['Total'] # Get total
    joves = row['Total 0-14']

    # Find the row in municipis with NOMMUNI = municipi
    municipi_row = municipis[municipis['NOMMUNI'] == municipi]
    
    if not municipi_row.empty:
        comarca = municipi_row['NOMCOMAR'].values[0]  # Get the value of NOMCOMAR

        # Find the row in comarques where NOMCOMAR matches
        comarca_row = comarques[comarques['NOMCOMAR'] == comarca]
        
        if not comarca_row.empty:
            # Update the 'Total' field in comarques
            comarques.loc[comarques['NOMCOMAR'] == comarca, 'Total'] += total_habitants_municipi
            comarques.loc[comarques['NOMCOMAR'] == comarca, 'Total 0-14'] += joves

comarques.loc[:, '% joves'] = (
    comarques['Total 0-14'] /
    comarques['Total']
)

# Convert merged DataFrame to GeoDataFrame
gdf = gpd.GeoDataFrame(comarques, geometry='geometry')

# Convert GeoDataFrame to GeoJSON format
geojson_data = gdf.__geo_interface__

# Create a Plotly figure
fig = go.Figure()

# Customize hover text to include both region name and % of young population with 2 decimal places
comarques['hover_text'] = comarques.apply(
    lambda row: f"Region: {row['NOMCOMAR']}<br>% joves: {row['% joves']:.2%}", axis=1
)

color_gradient = [
    [0, '#440154'],  # Dark Purple
    [0.1, '#482878'],  # Purple
    [0.2, '#3E4989'],  # Dark Blue
    [0.3, '#31688E'],  # Blue
    [0.4, '#26828E'],  # Cyan
    [0.5, '#1F9C89'],  # Light Cyan
    [0.6, '#6CDA6E'],  # Light Green
    [0.7, '#B5DE2B'],  # Yellow-Green
    [0.8, '#FDE724'],  # Yellow
    [1, '#FDE724']     # Bright Yellow
]

# Add the GeoJSON data to the figure with a color bar (legend)
fig.add_trace(go.Choroplethmapbox(
    geojson=geojson_data,
    locations=comarques.index,
    z=comarques['% joves'],  # Population data
    zmin=0.10,  # Set the minimum value for the color scale
    zmax=0.20,  # Set the maximum value for the color scale (e.g., 25% young population)
    colorscale=color_gradient,
    marker_line_width=1,  # Width of the borders
    marker_line_color='black',  # Color of the borders
    text=comarques['hover_text'],  # Tooltip text
    hoverinfo='text',
    colorbar=dict(
        title="Population",       # Title of the legend
        titleside="right",        # Title position
        tickvals=[0.10, 0.15, 0.2],  # Custom ticks (adjust according to your data)
        ticktext=["10%", "15%", "20%"],  # Custom labels
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
        'text': "Percentage of young people",  # Add your title here
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
