import csv
import json
import os
from statistics import mean
import pandas as pd
import numpy as np
from scipy.stats import pearsonr

# Constants and file paths - Update these paths with the actual path to your data directory
file_path_prefix = '/Users/eylai/Projects/llm-baseline/your/data/environment/'  # Update with actual path

precipitation_files = [
    os.path.join(file_path_prefix, 'monthly_precipitations_ashburnham.csv'),
    os.path.join(file_path_prefix, 'monthly_precipitations_amherst.csv'),
    os.path.join(file_path_prefix, 'monthly_precipitations_chatam.csv'),
    os.path.join(file_path_prefix, 'monthly_precipitations_boston.csv')
]
water_testing_files = [
    os.path.join(file_path_prefix, 'water-body-testing-2002.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2003.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2004.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2005.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2006.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2007.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2008.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2009.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2010.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2011.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2012.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2013.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2014.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2015.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2016.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2017.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2018.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2019.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2020.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2021.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2022.csv'),
    os.path.join(file_path_prefix, 'water-body-testing-2023.csv')
]

# Function to calculate average monthly precipitation for each year
def calculate_annual_precipitation(precip_files):
    monthly_data = {}
    
    for file in precip_files:
        if not os.path.exists(file):
            print(f"File not found: {file}")
            continue
        
        df = pd.read_csv(file)
        for _, row in df.iterrows():
            if isinstance(row['Year'], (str, int)) and str(row['Year']).isdigit():
                year = int(row['Year'])
                if year >= 2002 and year <= 2023:
                    if year not in monthly_data:
                        monthly_data[year] = []
                    monthly_data[year].append(sum(pd.to_numeric(row[['Jun', 'Jul', 'Aug', 'Sep']], errors='coerce')))
    
    return {year: mean(months) for year, months in monthly_data.items() if months}

# Function to calculate the exceedence rate for marine beaches
def calculate_exceedence_rate(water_files):
    exceedence_data = {}
    
    for file in water_files:
        if not os.path.exists(file):
            print(f"File not found: {file}")
            continue
        
        df = pd.read_csv(file)
        marine_beaches = df[df['Beach Type Description'] == 'Marine']
        for year in marine_beaches['Year'].unique():
            if int(year) in range(2002, 2024):
                yearly_data = marine_beaches[marine_beaches['Year'] == year]
                total_samples = yearly_data.shape[0]
                exceedences = yearly_data[yearly_data['Violation'].str.lower() == 'yes'].shape[0]
                
                if year not in exceedence_data:
                    exceedence_data[year] = []
                exceedence_data[year].append(exceedences / total_samples * 100 if total_samples > 0 else 0)
    
    return {year: mean(rates) for year, rates in exceedence_data.items()}

# Calculate the annual precipitation and exceedence rate
annual_precipitation = calculate_annual_precipitation(precipitation_files)
exceedence_rate = calculate_exceedence_rate(water_testing_files)

# Prepare the data for correlation calculation
common_years = set(annual_precipitation.keys()).intersection(exceedence_rate.keys())
rainfall_values = [annual_precipitation[year] for year in common_years]
exceedence_values = [exceedence_rate[year] for year in common_years]

# Ensure there are enough data points before calculating the Pearson correlation coefficient
if len(rainfall_values) >= 2 and len(exceedence_values) >= 2:
    correlation_coefficient, _ = pearsonr(rainfall_values, exceedence_values)
else:
    correlation_coefficient = None
    print("Not enough data points to calculate Pearson correlation.")

# Prepare the results JSON
results = {
    "environment-hard-1-1": "The percentage exceedence rate is calculated based on column 'Violation'",
    "environment-hard-1-2": annual_precipitation,
    "environment-hard-1-3": exceedence_rate,
    "environment-hard-1-4": correlation_coefficient if correlation_coefficient is not None else "Insufficient data for correlation"
}

# Print the JSON results
print(json.dumps(results, indent=4))