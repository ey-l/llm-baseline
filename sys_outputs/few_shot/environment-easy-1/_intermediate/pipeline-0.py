import pandas as pd
import json

# Load the 2018 water body testing data
data_2018 = pd.read_csv('/Users/eylai/Projects/llm-ds-flow/reference_systems/../../LLMBenchmark/data/environment/water-body-testing-2018.csv')

# Step environment-easy-1-1: Find the column name for the exceedance indicator
# Based on the data provided, the "Violation" column indicates if there was an exceedance or not
exceedance_col = 'Violation'

# Step environment-easy-1-2: Filter data for freshwater beaches in 2018
FRESHWATER_KEYWORDS = ["Fresh"]
freshwater_data_2018 = data_2018[
    (data_2018['Beach Type Description'].str.contains('|'.join(FRESHWATER_KEYWORDS), case=False, na=False))
]

# Step environment-easy-1-3: Count exceedance events
exceedances_2018 = freshwater_data_2018[exceedance_col].str.lower().str.contains("yes").sum()

# Prepare the answer dictionary
answers = {
    "environment-easy-1-1": exceedance_col,
    "environment-easy-1-2": len(freshwater_data_2018),
    "environment-easy-1-3": exceedances_2018,
    "environment-easy-1": exceedances_2018
}

# Print the outputs
print(json.dumps(answers, indent=4))