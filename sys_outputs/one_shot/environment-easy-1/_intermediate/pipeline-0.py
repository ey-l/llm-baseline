import pandas as pd
import json

# Step 1: Load the data from the file
file_path = '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2018.csv'
data = pd.read_csv(file_path)

answer = {
    "environment-easy-1-1": "Year",
    "environment-easy-1-2": "Beach Type Description",
    "environment-easy-1-3": "Violation"
}

# Step 2: Filter data for the year 2018, beach type 'Fresh', and violations 'yes'
data['Year'] = data['Year'].astype(str)  # Convert Year to string for comparison
filtered_data = data[(data['Year'] == '2018') &
                     (data['Beach Type Description'] == 'Fresh') &
                     (data['Violation'].str.lower() == 'yes')]

# Step 3: Count the number of bacterial exceedances
answer["environment-easy-1"] = len(filtered_data)

# Print the answers to the JSON array
print(json.dumps(answer, indent=4))