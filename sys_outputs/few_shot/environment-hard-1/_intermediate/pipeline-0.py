import pandas as pd
import numpy as np
import json
from scipy.stats import pearsonr

# Define file paths
precipitation_files = [
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitation_chatam.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitation_boston.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitations_ashburnham.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitation_ashburnham.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitations_amherst.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitations_chatam.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitations_boston.csv'
]

water_testing_files = [
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2015.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2014.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2016.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2002.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2003.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2017.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2013.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2007.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2006.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2012.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2004.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2010.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2011.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2005.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2020.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2008.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2009.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2021.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2023.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2022.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2019.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2018.csv'
]

# Define function to calculate total precipitation from June to September
def calculate_total_precipitation(file):
    df = pd.read_csv(file)
    df = df[df['Year'].between(2002, 2023)] # Filter for the years 2002 to 2023
    df['TotalRainfall_JuneSep'] = df[['Jun', 'Jul', 'Aug', 'Sep']].replace('M', np.nan).astype(float).sum(axis=1)
    return df.set_index('Year')['TotalRainfall_JuneSep']

# Collect precipitation data
total_precipitation = pd.concat([calculate_total_precipitation(file) for file in precipitation_files], axis=1)
total_precipitation.fillna(total_precipitation.mean(axis=1), inplace=True) # Fill NaN with the row mean
total_precipitation_mean = total_precipitation.mean(axis=1)

# Define function to calculate exceedence rate
def calculate_exceedence_rate(file):
    df = pd.read_csv(file)
    marine_beaches = df[df['Beach Type Description'] == 'Marine']
    exceedence_rate = marine_beaches.groupby('Year')['Violation'].apply(lambda x: (x == 'yes').sum() / len(x))
    return exceedence_rate

# Collect exceedence rate data
exceedence_rate = pd.concat([calculate_exceedence_rate(file) for file in water_testing_files], axis=0).groupby('Year').mean()

# Calculate correlation
common_years = total_precipitation_mean.index.intersection(exceedence_rate.index)
corr, _ = pearsonr(total_precipitation_mean.loc[common_years], exceedence_rate.loc[common_years])

print(json.dumps(
    {
        "environment-hard-1-1": ["Beach Type Description", "Violation"],
        "environment-hard-1-2": "Clean precipitation data and aggregate June, July, August, and September values for 2002-2023.",
        "environment-hard-1-3": corr,
        "environment-hard-1": corr
    },
    indent=4
))