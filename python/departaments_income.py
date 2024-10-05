import plotly.express as px
import pandas as pd

sous_df = pd.read_csv("alts_carrecs_sous.csv")

# Group by 'Departament' and aggregate the fields you need
result = sous_df.groupby('Departament').agg(
    Income=('Retribucio anual €', 'sum'),  # Sum of 'Income' for each department
    Number_of_people=('Departament', 'size'),  # Count occurrences of each department
    Alt_carrec=('Vinculacio', lambda x: (x == 'Alts càrrecs').sum())  # Count 'alt carrec' occurrences
).reset_index()

result.columns = ['Department', 'Income', 'Number of people', 'Alts carrec']

# Display the resulting DataFrame
#print(result)

fig = px.scatter(
    result, 
    x='Alts carrec',  # X-axis: Number of people in the department
    y='Number of people',  # Y-axis: Total income for each department
    size='Income',  # Bubble size based on the number of 'alt carrec'
    color='Department',  # Color based on the department
    hover_name='Department',  # Department name displayed on hover
    size_max=60,  # Set a max size for the bubbles
    title="Department Income and Number of People (Bubble Chart)"
)

# Customize the layout
fig.update_layout(
    xaxis_title="Alt carrec",
    yaxis_title="Number of people",
    paper_bgcolor='white',
    plot_bgcolor='white',
)

# Show the chart
fig.show()
