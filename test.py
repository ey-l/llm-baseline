import pandas as pd
import os
# File paths
files = [
    '../LLMBenchmark/data/environment/water-body-testing-2023.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2022.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2021.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2020.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2019.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2018.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2017.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2016.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2015.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2014.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2013.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2012.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2011.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2010.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2009.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2008.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2007.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2006.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2005.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2004.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2003.csv',
    '../LLMBenchmark/data/environment/water-body-testing-2002.csv'
]

# Function to calculate the exceedance rate for a given dataframe
def calculate_exceedance_rate(df):
    # Filter for freshwater beaches
    fresh_df = df[df['Beach Type Description'] == 'Fresh']
    # Calculate exceedance rate
    violation_count = fresh_df[fresh_df['Violation'].str.lower() == 'yes'].shape[0]
    total_count = fresh_df.shape[0]
    exceedance_rate = (violation_count / total_count) * 100 if total_count > 0 else 0
    return exceedance_rate

# Variable to store cumulative exceedance rate and count the years
cumulative_exceedance_rate = 0
years_count = 0

current_dir = os.path.dirname(os.path.abspath(__file__))
# Calculate historic average exceedance rate (2002-2022)
for file in files:
    # Load the data
    df = pd.read_csv(os.path.join(current_dir, file))
    # Extract year from filename (year is at the end of the file name for each file)
    year = int(file.split('-')[-1].split('.')[0])
    
    # Skip the 2023 file, it will be treated separately
    if year == 2023:
        continue
    
    # Calculate exceedance rate for the year
    rate = calculate_exceedance_rate(df)
    print(f"Exceedance rate for {year}: {rate:.2f}%")
    cumulative_exceedance_rate += rate
    years_count += 1

# Calculate the historic average (2002-2022)
print(f"Total years counted: {years_count}")
print(f"Cumulative exceedance rate (2002-2022): {cumulative_exceedance_rate:.2f}%")
historic_average = cumulative_exceedance_rate / years_count

# Calculate 2023 exceedance rate
df_2023 = pd.read_csv(os.path.join(current_dir, '../LLMBenchmark/data/environment/water-body-testing-2023.csv'))
exceedance_rate_2023 = calculate_exceedance_rate(df_2023)

# Calculate the percentage difference
percentage_difference = ((exceedance_rate_2023 - historic_average) / historic_average) * 100

# Print the result
print(f"Historic average exceedance rate (2002-2022): {historic_average:.2f}%")
print(f"2023 exceedance rate: {exceedance_rate_2023:.2f}%")
print(f"Percentage difference between 2023 exceedance rate and historic average: {(exceedance_rate_2023 - historic_average)}%")
print(f"Percentage difference between 2023 exceedance rate and historic average: {percentage_difference:.2f}%")