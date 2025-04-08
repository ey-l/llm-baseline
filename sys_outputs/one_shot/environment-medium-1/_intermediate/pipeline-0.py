import pandas as pd
import json
import glob

# Function to extract and calculate exceedance rate for a given year range
def calculate_exceedance_rate(files, start_year=None, end_year=None):
    exceedance_count = 0
    total_count = 0

    for file in files:
        df = pd.read_csv(file)
        
        # Filter for freshwater beaches
        df['Beach Type Description'] = df['Beach Type Description'].astype(str)
        freshwater_df = df[df['Beach Type Description'].str.contains("Fresh", case=False)]

        # Filter by year if needed
        if start_year and end_year:
            freshwater_df['Year'] = freshwater_df['Year'].astype(int)
            freshwater_df = freshwater_df[(freshwater_df['Year'] >= start_year) & (freshwater_df['Year'] <= end_year)]

        # Count exceedances and total samples
        exceedances = freshwater_df['Violation'].str.lower() == 'yes'
        exceedance_count += exceedances.sum()
        total_count += freshwater_df.shape[0]

    if total_count == 0:
        return None

    return (exceedance_count / total_count) * 100

# Get list of relevant files
all_files = glob.glob('/Users/eylai/Projects/llm-baseline/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-*.csv')

# Calculate historic average (2002-2022)
historic_files = [f for f in all_files if "2023" not in f]
historic_avg_exceedance_rate = calculate_exceedance_rate(historic_files, 2002, 2022)

# Calculate 2023 exceedance rate
files_2023 = [f for f in all_files if "2023" in f]
exceedance_rate_2023 = calculate_exceedance_rate(files_2023)

# Calculate difference
difference_exceedance_rate = None
if exceedance_rate_2023 is not None and historic_avg_exceedance_rate is not None:
    difference_exceedance_rate = exceedance_rate_2023 - historic_avg_exceedance_rate

# Print the answers
print(json.dumps({
    "environment-medium-1-1": "Freshwater beaches identified using 'Beach Type Description' field.",
    "environment-medium-1-2": historic_avg_exceedance_rate,
    "environment-medium-1-3": exceedance_rate_2023,
    "environment-medium-1-4": difference_exceedance_rate
}, indent=4))