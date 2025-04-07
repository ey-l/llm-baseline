"""
This script demonstrates a simple one-shot LLM approach to solve the LLMDS benchmark.
"""
import os
from utils import *


class Question:
    def __init__(self, question, data_dir):
        self.data_dir = data_dir
        self.id = question['id']
        self.query = question['query']
        self.answer = question['answer']
        self.file_names = self._get_file_names_in_dir() #question['data_sources']
        self.data_sources = [os.path.join(self.data_dir, ds) for ds in self.file_names]

    def _get_file_names_in_dir(self):
        """
        Get the file names in the data directory.
        :return: List of file names
        """
        file_names = os.listdir(self.data_dir)
        # Filter out non-CSV files
        file_names = [f for f in file_names if f.endswith('.csv')]
        # TODO: ** This is a temporary fix **
        # filter out "beaches_community.csv"
        file_names = [f for f in file_names if f != "beaches_community.csv"]
        return file_names
    
    def __repr__(self):
        return f"Question ID: {self.id}, Query: {self.query}, Answer: {self.answer}"

class BaselineLLM:
    def __init__(self):
        self.output_dir = None # to be set in run()
        self.question_output_dir = None # to be set in run()
        self.question_intermediate_dir = None # to be set in run()
    
    def _init_output_dir(self, output_dir:str, question:Question):
        """
        Initialize the output directory for the question.
        :param question: Question object
        """
        self.output_dir = output_dir
        question_output_dir = os.path.join(self.output_dir, question.id)
        if not os.path.exists(question_output_dir):
            os.makedirs(question_output_dir)
        self.question_output_dir = question_output_dir
        self.question_intermediate_dir = os.path.join(self.question_output_dir, '_intermediate')
        if not os.path.exists(self.question_intermediate_dir):
            os.makedirs(self.question_intermediate_dir)

    def generate_rag_plan(self, question:Question) -> str:
        """
        Generate a RAG plan for the LLM based on the question.
        TODO: ** This function is not in use right now **
        :param question: Question object
        :return: RAG plan string
        """
        rag_plan = f"""
        You are an experienced data scientist. 
        Your task is to answer the following question based on the provided data sources.
        Question: {question.query}
        Data files available: {question.data_sources}

        Think step-by-step carefully.
        Provide a list of things you need to see or check in the data files to answer the question.
        For example, you might need to check the column names, data types, specific values in the data files, or to locate a specific column in order to filter correctly.
        Then, provide the corresponding Python code to read the specific things you listed from the data sources. 
        ** Only provide code to read the data, DO NOT provide any code to process or analyze the data. **
        Mark the code with ````python` and ````python` to indicate the start and end of the code block.
        """
        return rag_plan
    
    def generate_error_handling_prompt(self, code_fp:str, error_fp:str) -> str:
        """
        Generate a prompt for the LLM to handle errors in the code.
        :param code_fp: Path to the code file
        :param error_fp: Path to the error file
        :return: Prompt string
        """
        with open(code_fp, 'r') as f:
            code = f.read()
        with open(error_fp, 'r') as f:
            errors = f.read()

        prompt = f"""
        Your task is to fix the following Python code based on the provided error messages.
        Code:
        {code}

        Errors:
        {errors}

        Please provide the fixed code. 
        Mark the code with ````python` and ````python` to indicate the start and end of the code block.
        """
        return prompt

    def get_input_data(self, data_sources) -> str:
        """
        Get the input data from the data sources.
        Naively read the first 10 rows of each data source.
        :param data_sources: List of data source file paths
        :return: Data as a string
        """
        data = ""
        for ds in data_sources:
            data += f"\nFile name: {ds}\n"
            data += get_table_string(ds)
            data += "\n"+ "="*20 + "\n"
        return data

    def generate_prompt(self, question:Question) -> str:
        """
        Generate a prompt for the LLM based on the question.
        :param question: Question object
        :return: Prompt string
        """
        # Generate the RAG plan
        data = self.get_input_data(question.data_sources)

        prompt = f"""
        Your task is to answer the following question based on the provided data sources.
        ID: {question.id}
        Question: {question.query}
        Data file names: {question.file_names}

        The following is a snippet of the data files:
        {data}

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

        # Save the prompt to a txt file
        prompt_fp = os.path.join(self.question_output_dir, f"prompt.txt")
        with open(prompt_fp, 'w') as f:
            f.write(prompt)
        print(f"Prompt saved to {prompt_fp}")
        return prompt

    def extract_response(self, question, response, try_number:int):
        """
        Process the LLM response.
        :param response: LLM response string
        :return: Processed response
        """
        json_fp = ""
        code_fp = ""
        # Save the full response to a txt file
        response_fp = os.path.join(self.question_output_dir, f"initial_response.txt")
        with open(response_fp, 'w') as f:
            f.write(response)
        print(f"Response saved to {response_fp}")

        # Assume the step-by-step plan is fixed after the first try
        if try_number == 0:
            # Extract the JSON array from the response
            json_response = extract_code(response, pattern=r'```json(.*?)```')
            #print("Extracted JSON:", json_response)
            # Save the JSON response to a file
            json_fp = os.path.join(self.question_output_dir, f"answer.json")
            with open(json_fp, 'w') as f:
                f.write(json_response)
            print(f"JSON response saved to {json_fp}")
        
        # Extract the code from the response
        code = extract_code(response, pattern=r'```python(.*?)```')
        #print("Extracted Code:", code)
        # Save the code to a file
        code_fp = os.path.join(self.question_output_dir, '_intermediate', f"pipeline-{try_number}.py") #{question.id}-{try_number}
        with open(code_fp, 'w') as f:
            f.write(code)
        print(f"Code saved to {code_fp}")

        return json_fp, code_fp

    def execute_code(self, question, code_fp, try_number:int):
        """
        Execute the code in the file and save the output.
        :param code_fp: Path to the code file
        :return: Execution result
        """
        # Execute the code and save error messages
        result = subprocess.run(
            ['python', code_fp],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Save the printed output of the code execution
        output_fp = os.path.join(self.question_intermediate_dir, f"pipeline-{try_number}_out.json")
        with open(output_fp, 'w') as f:
            f.write(result.stdout)

        # Save only compile/runtime errors
        error_fp = os.path.join(self.question_intermediate_dir, f"errors-{try_number}.txt")
        with open(error_fp, 'w') as f:
            f.write(result.stderr)

        return output_fp, error_fp
    
    def process_response(self, json_fp, output_fp, error_fp):
        """
        Process the response and fill in the JSON response with the execution result.
        :param question: Question object
        :param json_fp: Path to the JSON file
        :param output_fp: Path to the output file
        """
        # Load the JSON response
        try: 
            with open(json_fp, 'r') as f:
                response = json.load(f)
        except json.JSONDecodeError as e:
            print(f"** ERRORS ** decoding response JSON: {e}")
            return

        # Load the output file
        try: 
            with open(output_fp, 'r') as f:
                output = json.load(f)
        except json.JSONDecodeError as e:
            print(f"** ERRORS ** decoding output JSON: {e}")
            return

        # Fill in the JSON response with the execution result
        for step in response:
            id = step['id']
            if id in output:
                step['answer'] = output[id]
            else:
                step['answer'] = "No answer found."

        # Save the updated JSON response
        with open(json_fp, 'w') as f:
            json.dump(response, f, indent=4)
        print(f"Updated JSON response saved to {json_fp}")

    def run_one_shot(self, output_dir, question:Question) -> str:
        """
        This function demonstrates a simple one-shot LLM approach to solve the LLMDS benchmark.
        """
        self._init_output_dir(os.path.join(output_dir, 'one_shot'), question)
            
        # Generate the prompt
        prompt = self.generate_prompt(question)
        print("Prompt:", prompt)

        # Get the model's response
        messages=[
            {"role": "system", "content": "You are an experienced data scientist."},
            {"role": "user", "content": prompt}
        ]
        response = call_gpt(messages)
        print("Response:", response)

        # Process the response
        json_fp, code_fp = self.extract_response(question, response, try_number=0)

        # Execute the code (if necessary)
        output_fp, error_fp = self.execute_code(question, code_fp, try_number=0)
        # print("Execution Result:", result)

        # Check if errors were generated
        if os.path.getsize(error_fp) > 0:
            # TODO: Handle the error case for the few-shot LLM
            # For now, just print the error message
            print(f"** ERRORS ** found in {error_fp}. Skipping JSON update.")
        else:
            # Fill in JSON response with the execution result
            self.process_response(json_fp, output_fp, error_fp)

        return response
    
    def run_few_shot(self, output_dir, question:Question) -> str:
        """
        This function demonstrates a simple few-shot LLM approach to solve the LLMDS benchmark.
        """
        self._init_output_dir(os.path.join(output_dir, 'few_shot'), question)

        # Generate the prompt
        prompt = self.generate_prompt(question)
        print("Prompt:", prompt)

        messages=[
            {"role": "system", "content": "You are an experienced data scientist."},
        ]

        for try_number in range(5):
            messages.append({"role": "user", "content": prompt})
            # Get the model's response
            response = call_gpt(messages)
            print("Response:", response)
            messages.append({"role": "assistant", "content": response})

            # Process the response
            if try_number == 0:
                json_fp, code_fp = self.extract_response(question, response, try_number)
            else: _, code_fp = self.extract_response(question, response, try_number)

            # Execute the code (if necessary)
            output_fp, error_fp = self.execute_code(question, code_fp, try_number)
            # print("Execution Result:", result)

            if os.path.getsize(error_fp) > 0:
                prompt = self.generate_error_handling_prompt(code_fp, error_fp)
            else:
                # Fill in JSON response with the execution result
                self.process_response(json_fp, output_fp, error_fp)
                break

        return response
    
    
def load_questions(file_path, data_dir):
    """
    Load questions from a JSON file.
    :return: List of Question objects
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    return [Question(q, data_dir) for q in data]


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

    baseline_system = BaselineLLM()
    # Iterate through each question and generate a response
    for question in questions:
        print(question)
        response = baseline_system.run_one_shot(output_dir, question)
        print("\n" + "="*50 + "\n")
        response = baseline_system.run_few_shot(output_dir, question)
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    # get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '../../LLMBenchmark/data/environment')
    json_fp = os.path.join(current_dir, '../../LLMBenchmark/workload/environment-hard.json')
    output_dir = os.path.join(current_dir, '../sys_outputs')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Example usage
    main(json_fp, data_dir, output_dir)