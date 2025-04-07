import pandas as pd
import json
from pathlib import Path

def calculate_exceedance_rate(file_path, start_year=None, end_year=None):
    df = pd.read_csv(file_path)
    if start_year is not None and end_year is not None:
        df = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)]
    
    freshwater_df = df[df['Beach Type Description'] == 'Fresh']
    exceedances = freshwater_df[freshwater_df['Violation'].str.lower() == 'yes'].shape[0]
    total_samples = freshwater_df.shape[0]
    
    if total_samples == 0:
        return 0
    
    return (exceedances / total_samples) * 100

def main():
    # Specify the data directory
    data_dir = Path("/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/")

    # Calculate the exceedance rate for 2023
    exceedance_rate_2023 = calculate_exceedance_rate(data_dir / "water-body-testing-2023.csv")

    # Calculate the historic average exceedance rate from 2002 to 2022
    historical_exceedance_rates = []
    for year in range(2002, 2023):
        file_path = data_dir / f"water-body-testing-{year}.csv"
        rate = calculate_exceedance_rate(file_path)
        historical_exceedance_rates.append(rate)

    historic_average_exceedance_rate = sum(historical_exceedance_rates) / len(historical_exceedance_rates)

    # Calculate the difference
    difference = exceedance_rate_2023 - historic_average_exceedance_rate

    # Print the results
    results = {
        "environment-medium-1-1": exceedance_rate_2023,
        "environment-medium-1-2": historic_average_exceedance_rate,
        "environment-medium-1": difference
    }

    print(json.dumps(results, indent=4))

if __name__ == "__main__":
    main()