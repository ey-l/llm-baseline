import pandas as pd
import numpy as np
import json
from scipy.stats import pearsonr

# Step 1: Identify which communities are associated with marine beaches
precip_communities_df = pd.read_csv("/Users/eylai/Projects/llm-baseline/reference_systems/../../LLMBenchmark/data/environment/precipitations_beaches_community.csv")
marine_communities = precip_communities_df[precip_communities_df['Beach Type'] == 'Marine']['Community'].tolist()

# Print answer for environment-hard-1-1
answer1 = marine_communities

# Step 2: Calculate the sum of rainfall from June to September for Boston and Chatam from 2002 to 2023
boston_precip_df = pd.read_csv("/Users/eylai/Projects/llm-baseline/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitations_boston.csv")
chatam_precip_df = pd.read_csv("/Users/eylai/Projects/llm-baseline/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitations_chatam.csv")

# Filter for years 2002-2023
boston_precip_df = boston_precip_df[pd.to_numeric(boston_precip_df['Year'], errors='coerce').between(2002, 2023)]
chatam_precip_df = chatam_precip_df[pd.to_numeric(chatam_precip_df['Year'], errors='coerce').between(2002, 2023)]

# Calculate the sum for specified months
boston_precip_df[['Jun', 'Jul', 'Aug', 'Sep']] = boston_precip_df[['Jun', 'Jul', 'Aug', 'Sep']].apply(pd.to_numeric, errors='coerce')
boston_precip_df['Summer_Rainfall'] = boston_precip_df[['Jun', 'Jul', 'Aug', 'Sep']].sum(axis=1)
chatam_precip_df[['Jun', 'Jul', 'Aug', 'Sep']] = chatam_precip_df[['Jun', 'Jul', 'Aug', 'Sep']].apply(pd.to_numeric, errors='coerce')
chatam_precip_df['Summer_Rainfall'] = chatam_precip_df[['Jun', 'Jul', 'Aug', 'Sep']].sum(axis=1)

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
# Ensure rainfall and violation_rates are numeric
rainfall_boston = pd.to_numeric(boston_precip_df.set_index('Year')['Summer_Rainfall'], errors='coerce')
rainfall_chatam = pd.to_numeric(chatam_precip_df.set_index('Year')['Summer_Rainfall'], errors='coerce')
rainfall = pd.concat([rainfall_boston, rainfall_chatam], axis=1).sum(axis=1)  # Average rainfall for both locations
print(rainfall)
violation_rates = pd.to_numeric(violation_rates, errors='coerce')  # Align indices

# Calculate the Pearson correlation coefficient
correlation, _ = pearsonr(rainfall, violation_rates)

# Print answer for environment-hard-1
answer = correlation
print(correlation)
