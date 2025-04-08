import pandas as pd
import json
import os

# Function to calculate the percentage exceedance rate
def calculate_exceedance_rate(file_paths, start_year, end_year, organism_threshold):
    exceedance_rates = {}
    
    for file_path in file_paths:
        if os.path.exists(file_path):
            # Define column names according to the observed data pattern
            columns = ['Community Code', 'Community', 'County Code', 'County Description', 'Year', 'Sample Date', 
                       'Beach Name', 'Beach Type Description', 'Organism', 'Indicator Level', 'Violation']
            
            # Read the data
            df = pd.read_csv(file_path, names=columns, skiprows=1)
            
            # Correct data types
            df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
            df['Indicator Level'] = pd.to_numeric(df['Indicator Level'], errors='coerce')
            
            # Filter for fresh water beaches within the specific years
            freshwater_df = df[(df['Beach Type Description'] == 'Fresh') & 
                               (df['Year'].between(start_year, end_year))]
            
            # Calculate exceedance
            exceedances = freshwater_df[organism_threshold(freshwater_df)].shape[0]
            total_samples = freshwater_df.shape[0]
            
            # Calculate exceedance rate for the year
            for year in freshwater_df['Year'].unique():
                yearly_samples = freshwater_df[freshwater_df['Year'] == year]
                total_yearly_samples = yearly_samples.shape[0]
                yearly_exceedances = yearly_samples[organism_threshold(yearly_samples)].shape[0]                
                if total_yearly_samples > 0:
                    exceedance_rates[int(year)] = (yearly_exceedances / total_yearly_samples) * 100
    
    return exceedance_rates

# Organism exceedance threshold function for freshwater
def e_coli_exceedance(df):
    return df['Organism'].str.contains('E. Coli') & (df['Indicator Level'] > 235)

# All years to be considered
years = range(2002, 2023)
paths = [f"/Users/eylai/Projects/llm-baseline/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-{year}.csv" for year in years]

# Calculate the historic average exceedance rate
historical_rates = calculate_exceedance_rate(paths, 2002, 2022, e_coli_exceedance)
historic_average_rate = sum(historical_rates.values()) / len(historical_rates)

# Exceedance rate for 2023
rate_2023 = calculate_exceedance_rate(["/Users/eylai/Projects/llm-baseline/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2023.csv"], 2023, 2023, e_coli_exceedance)[2023]

# The difference in exceedance rates
difference = rate_2023 - historic_average_rate

# Print outputs
print(json.dumps({
    "environment-medium-1-1": "Violation",
    "environment-medium-1-2": "Exceedance if Indicator Level > 235 for E. Coli",
    "environment-medium-1-3": historical_rates,
    "environment-medium-1-4": {'2023': rate_2023},
    "environment-medium-1": difference
}, indent=4))