import json
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Load the JSON data
with open('data.json') as f:
    json_content = json.load(f)  # Ensure data is a list of lists

# Step 4: Convert the list of lists to a DataFrame
df = pd.DataFrame(json_content)

# Convert specific columns to their appropriate data types
df["Any"] = pd.to_numeric(df["Any"], errors='coerce')
df["Total Mensual"] = pd.to_numeric(df["Total Mensual"], errors='coerce')

# Example: Plot a simple scatter plot of Any and Total Mensuals
plt.figure(figsize=(6,4))
plt.scatter(df['Any'], df['Total Mensual'], color='blue', label='Sous')
plt.title('Sous per any')
plt.xlabel('Any')
plt.ylabel('Total Mensual')
plt.legend()
plt.show()
