import pandas as pd
import numpy as np
import json
from pathlib import Path
from scipy.stats import pearsonr

# Environment-hard-1-1: Determine which locations have marine beaches and which precipitation data to use
precipitation_communities = pd.read_csv(Path('/Users/eylai/Projects/llm-baseline/reference_systems/../../LLMBenchmark/data/environment/precipitations_beaches_community.csv'))
marine_beaches = precipitation_communities[precipitation_communities['Beach Type'] == 'Marine']['Community'].unique()

# Let's print a list of marine beach communities
print("environment-hard-1-1:", marine_beaches.tolist())

# Environment-hard-1-2: Calculate the total rainfall from June to September for Boston and Chatam
boston_precipitation = pd.read_csv(Path('/Users/eylai/Projects/llm-baseline/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitations_boston.csv'))
chatham_precipitation = pd.read_csv(Path('/Users/eylai/Projects/llm-baseline/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitations_chatam.csv'))

# Extract precipitation from June to September
boston_precipitation['JJA_Sep'] = boston_precipitation[['Jun', 'Jul', 'Aug', 'Sep']].sum(axis=1)
chatham_precipitation['JJA_Sep'] = chatham_precipitation[['Jun', 'Jul', 'Aug', 'Sep']].sum(axis=1)

# Print precipitation data for key years
print("environment-hard-1-2:", {"Boston": boston_precipitation[['Year', 'JJA_Sep']].to_dict('records'), "Chatham": chatham_precipitation[['Year', 'JJA_Sep']].to_dict('records')})

# Environment-hard-1-3: Compile exceedance rates from water-body tests
def extract_year_data(filename):
    df = pd.read_csv(Path(filename))
    df_marine = df[df['Beach Type Description'] == 'Marine']
    df_marine['Year'] = pd.to_datetime(df_marine['Sample Date']).dt.year
    df_marine['Violation'] = df_marine['Violation'].apply(lambda x: str(x).lower() == 'yes')
    exceedance_by_year = df_marine.groupby('Year').apply(lambda x: x['Violation'].sum() / x['Violation'].count())
    return exceedance_by_year

# List of filenames for water-body testing from 2002 to 2023
water_body_filenames = [
    'water-body-testing-2015.csv', 'water-body-testing-2014.csv', 'water-body-testing-2016.csv', 
    'water-body-testing-2002.csv', 'water-body-testing-2003.csv', 'water-body-testing-2017.csv', 
    'water-body-testing-2013.csv', 'water-body-testing-2007.csv', 'water-body-testing-2006.csv', 
    'water-body-testing-2012.csv', 'water-body-testing-2004.csv', 'water-body-testing-2010.csv', 
    'water-body-testing-2011.csv', 'water-body-testing-2005.csv', 'water-body-testing-2020.csv', 
    'water-body-testing-2008.csv', 'water-body-testing-2009.csv', 'water-body-testing-2021.csv', 
    'water-body-testing-2023.csv', 'water-body-testing-2022.csv', 'water-body-testing-2019.csv', 
    'water-body-testing-2018.csv'
]

exceedance_rates = pd.Series(dtype=float)

for filename in water_body_filenames:
    year_data = extract_year_data(f'/Users/eylai/Projects/llm-baseline/reference_systems/../../LLMBenchmark/data/environment/{filename}')
    exceedance_rates = exceedance_rates.add(year_data, fill_value=0)

# Print the calculated exceedance rates
print("environment-hard-1-3:", exceedance_rates.to_dict())

# Environment-hard-1-4: Calculate Pearson correlation

# Assumed matching of the year data with exceedance data
# Ensure both datasets cover the same years
boston_data = boston_precipitation.set_index('Year')
chatham_data = chatham_precipitation.set_index('Year')
input_years = boston_data.index.intersection(chatham_data.index).intersection(exceedance_rates.index)

boston_JJA_Sep = boston_data.loc[input_years]['JJA_Sep']
chatham_JJA_Sep = chatham_data.loc[input_years]['JJA_Sep']

average_JJA_Sep = (boston_JJA_Sep + chatham_JJA_Sep) / 2 if 'Boston' in marine_beaches and 'Chatham' in marine_beaches else boston_JJA_Sep if 'Boston' in marine_beaches else chatham_JJA_Sep

# Calculate Pearson correlation
pearson_corr, _ = pearsonr(average_JJA_Sep, exceedance_rates.loc[input_years])

# Print the final result
print(json.dumps({
    "environment-hard-1": pearson_corr
}, indent=4))