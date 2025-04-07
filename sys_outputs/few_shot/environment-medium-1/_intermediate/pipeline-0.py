import pandas as pd
import json
from glob import glob

# Path to the data files for water body testing
data_path = '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/'

# Identify all relevant water body testing files
files = glob(data_path + 'water-body-testing-*.csv')

# Define a function to calculate the exceedance rate for a given year
def calculate_exceedance_rate(year, df):
    fresh_water = df[df['Beach Type Description'].str.strip().str.lower() == 'fresh']
    exceedances = fresh_water[fresh_water['Violation'].str.strip().str.lower() == 'yes'].shape[0]
    total = fresh_water.shape[0]
    return 100 * exceedances / total if total != 0 else 0

# Calculate the historical average exceedance rate from 2002 to 2022
historical_rates = []
for file in files:
    year = int(file.split('-')[-1].split('.')[0])  # Extract year from file name, handle properly
    if 2002 <= year <= 2022:
        df = pd.read_csv(file)
        exceedance_rate = calculate_exceedance_rate(year, df)
        historical_rates.append(exceedance_rate)
historical_average = sum(historical_rates) / len(historical_rates)

# Calculate the exceedance rate for 2023
df_2023 = pd.read_csv(data_path + 'water-body-testing-2023.csv')
exceedance_rate_2023 = calculate_exceedance_rate(2023, df_2023)

# Calculate the difference
difference = exceedance_rate_2023 - historical_average

# Output the answer
answer = {
    "environment-medium-1": difference
}

print(json.dumps(answer, indent=4))