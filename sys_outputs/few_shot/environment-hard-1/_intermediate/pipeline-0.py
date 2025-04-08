import pandas as pd
import numpy as np
import json
from scipy.stats import pearsonr

# Step 1: Identify which communities are associated with marine beaches
precip_communities_df = pd.read_csv("/Users/eylai/Projects/llm-baseline/reference_systems/../../LLMBenchmark/data/environment/precipitations_beaches_community.csv")
marine_communities = precip_communities_df[precip_communities_df['Beach Type'] == 'Marine']['Community'].tolist()

# Print answer for environment-hard-1-1
answer1 = marine_communities

# Step 2: Calculate the sum of rainfall from June to September for Boston from 2002 to 2023
boston_precip_df = pd.read_csv("/Users/eylai/Projects/llm-baseline/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitations_boston.csv")

# Filter for years 2002-2023
boston_precip_df = boston_precip_df[pd.to_numeric(boston_precip_df['Year'], errors='coerce').between(2002, 2023)]

# Calculate the sum for specified months
boston_precip_df['Summer_Rainfall'] = boston_precip_df[['Jun', 'Jul', 'Aug', 'Sep']].apply(pd.to_numeric, errors='coerce').sum(axis=1)

# Print answer for environment-hard-1-2
answer2 = json.loads(boston_precip_df[['Year', 'Summer_Rainfall']].to_json(orient='records'))

# Step 3: Calculate the percentage exceedence rate for each year for marine beaches from 2002 to 2023
water_body_files = [
    "water-body-testing-2015.csv", "water-body-testing-2014.csv", 
    "water-body-testing-2016.csv", "water-body-testing-2002.csv",
    "water-body-testing-2003.csv", "water-body-testing-2017.csv",
    "water-body-testing-2013.csv", "water-body-testing-2007.csv",
    "water-body-testing-2006.csv", "water-body-testing-2012.csv",
    "water-body-testing-2004.csv", "water-body-testing-2010.csv",
    "water-body-testing-2011.csv", "water-body-testing-2005.csv",
    "water-body-testing-2020.csv", "water-body-testing-2008.csv",
    "water-body-testing-2009.csv", "water-body-testing-2021.csv",
    "water-body-testing-2023.csv", "water-body-testing-2022.csv",
    "water-body-testing-2019.csv", "water-body-testing-2018.csv"
]

dataframes = []
for file in water_body_files:
    df = pd.read_csv(f"/Users/eylai/Projects/llm-baseline/reference_systems/../../LLMBenchmark/data/environment/{file}")
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df = df[df['Beach Type Description'] == 'Marine']
    df = df[df['Year'].between(2002, 2023)]
    df['Violation'] = df['Violation'].str.lower().map({'yes': True, 'no': False})
    dataframes.append(df)

marine_df = pd.concat(dataframes, ignore_index=True)
violation_rates = marine_df.groupby('Year')['Violation'].mean().multiply(100)  # Percentage of exceedence

# Print answer for environment-hard-1-3
answer3 = violation_rates.to_dict()

# Step 4: Calculate Pearson correlation
rainfall = boston_precip_df.set_index('Year')['Summer_Rainfall']
violation_rates = violation_rates.reindex(rainfall.index)  # Align indices
correlation, _ = pearsonr(rainfall, violation_rates)

# Print answer for environment-hard-1
answer = correlation

# Print all answers
print(json.dumps(
    {
        "environment-hard-1-1": answer1, 
        "environment-hard-1-2": answer2, 
        "environment-hard-1-3": answer3,
        "environment-hard-1": answer
    }, indent=4
))