import pandas as pd
import json

def count_exceedances(file_path, year, beach_type, violation_col='Violation', beach_type_col='Beach Type Description'):
    # Load the dataset
    data = pd.read_csv(file_path)

    # Filter for the desired year
    data['Year'] = data['Year'].astype(str)
    year_data = data[data['Year'] == str(year)]

    # Further filter for the desired beach type
    fresh_beach_data = year_data[year_data[beach_type_col] == beach_type]

    # Count the exceedances
    exceedances = fresh_beach_data[violation_col].str.lower() == 'yes'

    return exceedances.sum()

# Define file paths
water_body_testing_2018_file = '/Users/eylai/Projects/llm-baseline/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2018.csv'

# Get the number of bacterial exceedances for freshwater beaches in 2018
number_of_exceedances = count_exceedances(water_body_testing_2018_file, 2018, 'Fresh')

print(number_of_exceedances)