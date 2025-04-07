"""
This module imports the necessary packages and functions for the reference_systems module.
"""
import os
import sys
import re
import random
import numpy as np
import pandas as pd
import json
import time
import subprocess

from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("MY_OPENAI_API_KEY"))

def call_gpt(messages, model="gpt-4o"):
    
    max_retries = 5
    retry_count = 0
    while retry_count < max_retries:
        try:
            ################### use to be openai.Completion.create(), now ChatCompletion ###################
            ################### also parameters are different, now messages=, used to be prompt= ###################
            # note deployment_id=... not model=...
            result = client.chat.completions.create(
                model=model,
                messages=messages,
            )
            
            break # break out of while loop if no error
        
        except Exception as e:
            print(f"An error occurred: {e}. Retrying...")
            retry_count += 1
            time.sleep(10 * retry_count)  # Wait 
            
    if retry_count == max_retries:
        print("Max retries reached. Skipping...")
        res = "Max retries reached. Skipping..."
    else:
        #print(result)
        try:
            res = result.choices[0].message.content
        except Exception as e:
            print("Error:", e)
            res = ""
        #print(res)
    return res

def get_table_string(fp, row_limit = 100):
    try: 
        table = pd.read_csv(fp, engine='python', on_bad_lines='warn')
        if len(table) <= row_limit:
            return table.to_csv()
        # Randomly sample the table
        table_string = table.sample(n=min(10, len(table)), random_state=1)
        # Convert the table to a  comma-separated string
        table_string = table_string.to_csv()
        return table_string
    
        #return table.head(find_number_rows(table, token_limit)).to_csv(sep='|', index=False)
    except Exception as e:
        print("Error:", e) 
        return ""

def extract_code(response, pattern=r'```python(.*?)```'):
        """
        Extract the code from the LLM response.
        :param response: LLM response string
        :return: Extracted code string
        """
        # Assuming the code is marked with ````python` and ````python`
        code = re.search(pattern, response, re.DOTALL)
        if code:
            return code.group(1).strip()
        return ""

def find_number_rows(table, token_limit = 900):
    # Get the first row of the table
    m = table.iloc[[0]].to_csv(sep='|', index=False)
    m = re.split('||\s+', m)
    m=[x for x in m if x != '' and x != '|']
    n_row = int(token_limit/len(m))
    if n_row < 1: return 1
    return n_row

if __name__ == "__main__":
    # Example usage
    prompt = [
        {"role": "user", "content": "Hello, how are you?"}
    ]
    response = call_gpt(prompt)
    print("Response:", response)