import pandas as pd
import numpy as np
import json
from glob import glob

# Step 1: Determine which beaches are Marine
precip_communities_df = pd.read_csv("/Users/eylai/Projects/llm-baseline/reference_systems/../../LLMBenchmark/data/environment/precipitations_beaches_community.csv")
marine_communities = precip_communities_df[precip_communities_df["Beach Type"] == "Marine"]["Community"].unique()

# Step 2: Extract rainfall amounts for Marine beach communities
def extract_marine_data(file_name, communities):
    df = pd.read_csv(file_name)
    df = df[df["Year"].apply(lambda x: str(x).isdigit())]  # filter non-numeric years
    df["Year"] = df["Year"].astype(int)
    df.set_index("Year", inplace=True)
    marine_df = df.loc[:, ["Jun", "Jul", "Aug", "Sep"]].loc[df.index.isin(range(2002, 2024))]
    marine_df.replace("M", np.nan, inplace=True)
    marine_df = marine_df.apply(pd.to_numeric)
    marine_df["total_precip"] = marine_df.sum(axis=1, skipna=True)
    return marine_df

boston_precip = extract_marine_data("/Users/eylai/Projects/llm-baseline/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitations_boston.csv", marine_communities)
chatam_precip = extract_marine_data("/Users/eylai/Projects/llm-baseline/reference_systems/../../LLMBenchmark/data/environment/monthly_precipitations_chatam.csv", marine_communities)

# Averaging precipitation values for each year for the Marine beaches
combined_precip = pd.concat([boston_precip[["total_precip"]], chatam_precip[["total_precip"]]], axis=1)
combined_precip.columns = ["boston_precip", "chatam_precip"]
combined_precip["average_precip"] = combined_precip.mean(axis=1, skipna=True)

# Step 3: Calculate percentage exceedance rate for Marine beaches
def calculate_exceedence_rate(file_pattern):
    files = glob(file_pattern)
    exceedence_data = []

    for file in files:
        df = pd.read_csv(file)
        df = df[(df["Beach Type Description"] == "Marine") & (df["Violation"] == "yes")]
        violation_counts = df.groupby("Year").size()
        exceedence_data.append(violation_counts)

    all_exceedences = pd.concat(exceedence_data, axis=1)
    all_exceedences = all_exceedences.sum(axis=1)
    total_counts = pd.concat([pd.read_csv(file) for file in files])
    total_counts = total_counts[total_counts["Beach Type Description"] == "Marine"].groupby("Year").size()
    percentage_exceedence = (all_exceedences / total_counts) * 100
    return percentage_exceedence

marine_exceedence_rate = calculate_exceedence_rate("/Users/eylai/Projects/llm-baseline/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-*.csv")

# Align both dataframes on the same index
aligned_precipitation = combined_precip["average_precip"].reindex(marine_exceedence_rate.index)
aligned_exceedence_rate = marine_exceedence_rate.reindex(combined_precip.index)

# Step 4: Calculate Pearson correlation
pearson_corr = aligned_precipitation.corr(aligned_exceedence_rate, method='pearson')

# Print results in the required JSON format
print(json.dumps({
    "environment-hard-1-1": marine_communities.tolist(),
    "environment-hard-1-2": combined_precip["average_precip"].tolist(),
    "environment-hard-1-3": marine_exceedence_rate.to_dict(),
    "environment-hard-1": pearson_corr
}, indent=4))