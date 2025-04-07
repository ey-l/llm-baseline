"""
This script generates a deep research prompt.
"""
import os
from utils import *
from baseline import *

def generate_deep_prompt(question:Question):
    
    """
    Generate a prompt for the LLM based on the question.
    :param question: Question object
    :return: Prompt string
    """
    
    prompt = f"""
    Your task is to answer the following question based on the provided data sources.
    ID: {question.id}
    Question: {question.query}
    Data file names: {question.file_names}

    Find the data on the web.

    Now think step-by-step carefully. 
    First, provide a step-by-step reasoning of how you would arrive at the correct answer.
    Do not assume the data files are clean or well-structured (e.g., missing values, inconsistent data type in a column).
    Do not assume the data type of the columns is what you see in the data snippet (e.g., 2012 in Year could be a string, instead of an int). So you need to convert it to the correct type if your subsequent code relies on the correct data type (e.g., cast two columns to the same type before joining the two tables).
    You have to consider the possible data issues observed in the data snippet and how to handle them.
    Output the steps in a JSON format with the following keys:
    - id: the step number, starts with {question.id}, which is the main task, and continue with the subtasks from 1, for example {question.id}-1, {question.id}-2, etc.
    - query: the question the step is trying to answer. Copy down the question from above for the main task.
    - data_sources: the data sources you need to check to answer the question. Include all the file names you need for the main task.
    For example, a JSON object for the task might look like this:
    {[{
        "id": "{question.id}",
        "query": "What is the exceedance rate in 2022?",
        "data_sources": ["water-body-testing-2022.csv"]
    },{
        "id": "{question.id}-1",
        "query": "What is the column name for the exceedance rate?",
        "data_sources": ["water-body-testing-2022.csv"]
    }]}
    You can have multiple steps, and each step should be a JSON object.
    Your output for this task should be a JSON array of JSON objects.
    Mark the JSON array with ````json` and ````json` to indicate the start and end of the code block.

    Then, provide the corresponding Python code to extract the answer from the data sources. 
    The data sources you may need to answer the question are: {question.data_sources}
    
    If possible, print the answer (in a JSON format) to each step you provided in the JSON array using the print() function.
    Use "id" as the key to print the answer.
    For example, if you have an answer to {question.id}-1, {question.id}-2, and {question.id} (i.e., the final answer), you should print it like this:
    print(json.dumps(
    {{"{question.id}-1": answer1, 
    "{question.id}-2": answer2, 
    "{question.id}": answer
    }}, indent=4))
    You can find a suitable indentation for the print statement. Always import json at the beginning of your code.

    Mark the code with ````python` and ````python` to indicate the start and end of the code block.
    """

    return prompt

def main(question_json_fp:str = None, data_dir:str = None, output_dir:str = None):
    """
    Main function to run the one-shot LLM approach.
    :param question_json_fp: Path to the JSON file containing questions
    :param data_dir: Directory containing the data files
    :param output_dir: Directory to save the output files
    """
    # Load the questions
    if question_json_fp is None:
        print("No question JSON file provided. Exiting.")
        return
    questions = load_questions(question_json_fp, data_dir)

    for question in questions:
        print(question)
        # Generate the prompt
        prompt = generate_deep_prompt(question)
        print(prompt)

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '../../LLMBenchmark/data/environment')
    json_fp = os.path.join(current_dir, '../../LLMBenchmark/workload/environment-hard.json')
    output_dir = os.path.join(current_dir, '../sys_outputs')
    
    main(json_fp, data_dir, output_dir)