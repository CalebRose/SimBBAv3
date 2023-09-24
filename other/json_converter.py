import pandas as pd
import json

# Read the CSV file into a DataFrame
df = pd.read_csv("abbreviations.csv")

# Create a dictionary with keys from the first column and values from the second column
result_dict = dict(zip(df.iloc[:, 1], df.iloc[:, 0]))

# Convert the dictionary to a JSON object
json_data = json.dumps(result_dict)

# To save the JSON data to a file
with open("abbreviations.json", "w") as f:
    f.write(json_data)
