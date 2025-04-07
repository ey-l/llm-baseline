import pandas as pd
import numpy as np
import json
from scipy.stats import pearsonr

# Helper function to clean rainfall data
def clean_rainfall_data(file_paths):
    data_frames = []
    for path in file_paths:
        df = pd.read_csv(path, skipinitialspace=True)
        df = df.replace("M", np.nan)
        # Filter out non-numeric Year rows
        df = df[df['Year'].apply(lambda x: x.isdigit())]
        df['Year'] = df['Year'].astype(int)  # Ensure Year is an integer
        data_frames.append(df[['Year', 'Jun', 'Jul', 'Aug', 'Sep']])
    return pd.concat(data_frames, ignore_index=True)

# Helper function to calculate monthly precipitation totals
def calculate_precipitation_total(df):
    df = df.dropna().copy()
    df['Total_Precipitation'] = df[['Jun', 'Jul', 'Aug', 'Sep']].astype(float).sum(axis=1)
    return df[['Year', 'Total_Precipitation']]

# Load beaches_community to identify marine communities
beaches_community_path = '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/beaches_community.csv'
beaches_df = pd.read_csv(beaches_community_path)
marine_communities = beaches_df[beaches_df['Beach Type'] == 'Marine']['Community']

# Load and clean precipitation data
precipitation_paths = [
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitation_chatam.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitation_boston.csv'
]
rainfall_data = clean_rainfall_data(precipitation_paths)
rainfall_total = calculate_precipitation_total(rainfall_data)

# Helper function to extract exceedence rates from water-body-testing data
def extract_exceedence_rate(file_paths, marine_communities):
    exceedence_data = []

    for path in file_paths:
        water_data = pd.read_csv(path)
        water_data = water_data[water_data['Beach Type Description'] == 'Marine']
        water_data = water_data[water_data['Community'].isin(marine_communities)]
        exceedences = water_data[water_data['Violation'] == 'yes'].groupby('Year').size()
        total_tests = water_data.groupby('Year').size()
        rates = (exceedences / total_tests).reindex(total_tests.index, fill_value=0) * 100
        exceedence_data.append(rates)

    total_exceedence_data = pd.concat(exceedence_data).groupby(level=0).mean().reset_index(name='Exceedence_Rate')
    return total_exceedence_data

# List all relevant water body testing files
water_testing_paths = [
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2002.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2003.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2004.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2005.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2006.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2007.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2008.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2009.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2010.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2011.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2012.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2013.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2014.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2015.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2016.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2017.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2018.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2019.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2020.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2021.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2022.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2023.csv'
]

# Get exceedence rate data
exceedence_rate_data = extract_exceedence_rate(water_testing_paths, marine_communities)

# Merge the rainfall data with the exceedence rate data
merged_data = pd.merge(rainfall_total, exceedence_rate_data, on='Year')

if len(merged_data) > 1:
    # Calculate Pearson correlation
    correlation, _ = pearsonr(merged_data['Total_Precipitation'], merged_data['Exceedence_Rate'])
else:
    correlation = None

# Creating the solution output as a dictionary
solution = {
    "environment-hard-1-1": marine_communities.tolist(),
    "environment-hard-1-4": correlation,
    "environment-hard-1": correlation
}

# Print the solution
print(json.dumps(solution, indent=4))