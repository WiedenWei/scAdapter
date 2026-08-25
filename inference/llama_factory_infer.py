import json
from openai import OpenAI
import sys

def run_inference(test_data_path, api_base_url, api_key="0"):

    try:
        client = OpenAI(api_key=api_key, base_url=api_base_url)
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")
        return
    try:
        with open(test_data_path, 'r', encoding='utf-8') as f_test:
            test_lines = f_test.readlines()
    except FileNotFoundError as e:
        print(f"Error: Could not find a required file. {e}")
        return
    
    for i, line in enumerate(test_lines):
        try:
            data = json.loads(line.strip())
            messages = data['messages']
            
            result = client.chat.completions.create(
                messages=messages,
                model="openai/gpt-oss-20b"
            )
            
            raw_prediction = result.choices[0].message.content.strip()
            model_prediction = raw_prediction.replace("analysisassistantfinal", "").strip()
            print(model_prediction)

        except json.JSONDecodeError:
            print(f"Warning: Skipping malformed JSON on line {i+1}.")
        except Exception as e:
            print(f"An error occurred while processing sample {i+1}: {e}")

if __name__ == '__main__':
    TEST_DATASET_FILE = sys.argv[1]
    BASE_URL = "http://0.0.0.0:8000/v1"
    run_inference(TEST_DATASET_FILE, BASE_URL)
