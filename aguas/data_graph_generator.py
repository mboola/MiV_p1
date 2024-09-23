import matplotlib.pyplot as plt
import seaborn as sns
import json
import pandas as pd

# Step 1: Load the JSON data
with open('vertidos_aguas.json') as f:
    json_content = json.load(f)  # Ensure data is a list of lists

# Step 2: Extract the 'data' section
data = json_content.get('data', [])  # Default to an empty list if 'data' key is not found

# Step 3: Define the column names for the DataFrame
columns = [
    "ID", "Unique Identifier", "Field 1", "Timestamp 1", "Field 2", "Timestamp 2", "Field 3", "Metadata", 
    "Permit Number", "Location", "Company Name", "Activity", "Facility Description", 
    "Discharge Type", "Discharge Location", "X Coordinate", "Y Coordinate", "River Name", 
    "Boolean Field", "Measurement", "Latitude", "Field 4", "Field 5"
]

# Step 4: Convert the list of lists to a DataFrame
df = pd.DataFrame(data, columns=columns)

df['River Name'] = df['River Name'].str.lower()  # Convert all river names to lowercase
river_counts = df['River Name'].value_counts()

#Plot the data
plt.figure(figsize=(12, 8))
river_counts.plot(kind='bar', color='skyblue')
plt.title('Number of Times Each River is Mentioned')
plt.xlabel('River Name')
plt.ylabel('Number of Mentions')
plt.xticks(rotation=90)
plt.tight_layout()  # Adjust layout to make room for the x-axis labels

# Show the plot
plt.show()

# Step 6: Creating Visualizations

# Convert specific columns to their appropriate data types
df["X Coordinate"] = pd.to_numeric(df["X Coordinate"], errors='coerce')
df["Y Coordinate"] = pd.to_numeric(df["Y Coordinate"], errors='coerce')
df["Measurement"] = pd.to_numeric(df["Measurement"], errors='coerce')
df["Latitude"] = pd.to_numeric(df["Latitude"], errors='coerce')

# Example: Plot a simple scatter plot of X and Y coordinates (UTM Coordinates)
plt.figure(figsize=(6,4))
plt.scatter(df['X Coordinate'], df['Y Coordinate'], color='blue', label='Location')
plt.title('Facility Location (UTM Coordinates)')
plt.xlabel('X Coordinate (UTM)')
plt.ylabel('Y Coordinate (UTM)')
plt.legend()
plt.show()

# Bar Chart (e.g., GDP over Years)
#plt.figure(figsize=(6,4))
#sns.barplot(x=df['years'], y=df['gdp'], palette='Blues_d')
#plt.title('GDP Over Years')
#plt.xlabel('Years')
#plt.ylabel('GDP in Trillions')
#plt.show()

# Scatter Plot (e.g., Population vs GDP)
#plt.figure(figsize=(6,4))
#plt.scatter(df['population'], df['gdp'], color='green', label='Population vs GDP')
#plt.title('Population vs GDP')
#plt.xlabel('Population')
#plt.ylabel('GDP in Trillions')
#plt.legend()
#plt.show()
