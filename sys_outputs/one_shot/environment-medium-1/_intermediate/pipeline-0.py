import pandas as pd
import json

# Data paths (note: in a real scenario you would adjust these paths)
data_files = {
    year: f"/Users/eylai/Projects/llm-baseline/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-{year}.csv"
    for year in range(2002, 2024)
}

def calculate_exceedance_rate(data_files, start_year, end_year=None):
    violation_records = 0
    total_records = 0
    
    for year, file_path in data_files.items():
        if year < start_year:
            continue
        if end_year and year > end_year:
            break

        # Load data
        df = pd.read_csv(file_path)

        # Ensure 'Year' and 'Beach Type Description' are of the correct type
        df['Year'] = df['Year'].astype(str).str.extract('(\d+)').astype(int)
        df['Beach Type Description'] = df['Beach Type Description'].astype(str)
        
        # Filter freshwater beaches
        freshwater_beaches = df[df['Beach Type Description'].str.lower() == 'fresh']
        
        # Count violations
        violations = freshwater_beaches['Violation'].str.lower() == 'yes'
        violation_records += violations.sum()
        total_records += freshwater_beaches.shape[0]

    if total_records == 0:
        return 0

    # Calculate the rate
    return (violation_records / total_records) * 100

# Calculate percentage exceedance rate for the specified periods
historic_exceedance_rate = calculate_exceedance_rate(data_files, 2002, 2022)
rate_2023 = calculate_exceedance_rate(data_files, 2023, 2023)

# Calculate difference
difference = rate_2023 - historic_exceedance_rate

# Prepare answer result
result = {
    "environment-medium-1-1": "The relevant columns are 'Beach Type Description' and 'Violation'. They indicate beach type and whether there was an exceedance violation, respectively.",
    "environment-medium-1-2": "Handle missing or inconsistent values by ensuring all relevant fields (Year, Beach Type Description, Violation) are correctly typed and filtered for analysis.",
    "environment-medium-1-3": rate_2023,
    "environment-medium-1-4": historic_exceedance_rate,
    "environment-medium-1": difference
}

# Print the result
print(json.dumps(result, indent=4))