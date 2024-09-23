import csv
import json

# Define input CSV file and output JSON file paths
csv_file_path = 'input.csv'
json_file_path = 'output.json'

# Initialize an empty list to store rows
data = []

# Open the CSV file for reading
with open(csv_file_path, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)  # Use DictReader to map headers to values
    for row in csv_reader:
        data.append(row)  # Append each row (as a dictionary) to the list

# Write the list of dictionaries to a JSON file
with open(json_file_path, mode='w') as json_file:
    json.dump(data, json_file, indent=4)  # Use indent=4 for pretty printing
