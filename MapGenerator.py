import pandas as pd
import geopandas as gpd
from shapely import wkt
import plotly.graph_objects as go

# Load the CSV file
file_path = "comarques_catalunya.csv"  # Replace with your actual file path
data = pd.read_csv(file_path)

# Convert the 'Georeferència' column (which is WKT) to actual geometries
data['geometry'] = data['Georeferència'].apply(wkt.loads)

# Convert to a GeoDataFrame
gdf = gpd.GeoDataFrame(data, geometry='geometry')

# Convert GeoDataFrame to GeoJSON format
geojson_data = gdf.__geo_interface__

# Create a Plotly figure
fig = go.Figure()

# Add the GeoJSON data to the figure
fig.add_trace(go.Choroplethmapbox(
    geojson=geojson_data,
    locations=gdf.index,
    z=[1]*len(gdf),  # Dummy variable for coloring (1 for all)
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
    ],
    dragmode=False,  # Disable drag mode
)

# Show the figure
fig.show()
