import pandas as pd
import scipy.stats as stats
import json

def read_and_concat_precipitation_data(files):
    df_list = []
    for file in files:
        df = pd.read_csv(file)
        # Convert 'Year' to string to handle any data type inconsistency across files
        df['Year'] = df['Year'].astype(str)  
        df_list.append(df)
    combined_df = pd.concat(df_list, ignore_index=True)
    return combined_df

def read_and_concat_water_testing_data(files):
    df_list = []
    for file in files:
        df = pd.read_csv(file)
        # Filter only the marine beaches
        df = df[df['Beach Type Description'].str.lower() == 'marine']
        df['Year'] = df['Year'].astype(str)  
        df_list.append(df)
    combined_df = pd.concat(df_list, ignore_index=True)
    return combined_df

# Load the precipitation data
precipitation_files = [
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitation_chatam.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitation_boston.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitations_ashburnham.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitation_ashburnham.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitations_amherst.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitation_amherst.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitations_chatam.csv',
    '/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitations_boston.csv'
]

# Handling precipitation data from June to September
precip_df = read_and_concat_precipitation_data(precipitation_files)
precip_df = precip_df.replace('M', pd.NA).dropna(subset=['Jun', 'Jul', 'Aug', 'Sep'])
precip_df[['Jun', 'Jul', 'Aug', 'Sep']] = precip_df[['Jun', 'Jul', 'Aug', 'Sep']].apply(pd.to_numeric, errors='coerce')
precip_df['Year'] = precip_df['Year'].astype(str)
precip_df['TotalSummerRain'] = precip_df[['Jun', 'Jul', 'Aug', 'Sep']].sum(axis=1)

# Load the water quality testing data
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

marine_df = read_and_concat_water_testing_data(water_testing_files)
marine_df['Year'] = marine_df['Year'].astype(str)

# Calculate percentage exceedence rate for marine beaches
exceedence_rate = marine_df.groupby('Year')['Violation'].apply(lambda x: (x == 'yes').mean() * 100).reset_index()
exceedence_rate['Year'] = exceedence_rate['Year'].astype(str)

# Merging precipitation and exceedence rate data on year
correlation_df = pd.merge(precip_df[['Year', 'TotalSummerRain']], exceedence_rate, on='Year')

# Calculating Pearson correlation
correlation_value, _ = stats.pearsonr(correlation_df['TotalSummerRain'], correlation_df['Violation'])

print(json.dumps(
    {"environment-hard-1-1": "The 'Violation' column indicates exceedence.",
     "environment-hard-1-2": "'Jun', 'Jul', 'Aug', and 'Sep' columns contain the rainfall data for those months.",
     "environment-hard-1": correlation_value
    }, indent=4))