import dspy
import json
import os

class ExtractData(dspy.Signature):
    text: str = dspy.InputField()
    textual_data: str = dspy.InputField()
    json_output: str = dspy.OutputField(desc="Respond with JSON only, without any additional text, code block markers, or explanations.")

def process_markdown_with_dspy(markdown_file_path, output_json_file, prompt):
    # Load the content of the markdown file
    try:
        with open(markdown_file_path, 'r', encoding='utf-8') as md_file:
            markdown_content = md_file.read()
    except FileNotFoundError:
        print(f"Error: The file '{markdown_file_path}' was not found.")
        return
    except Exception as e:
        print(f"Error reading the markdown file: {e}")
        return

    # Initialize the DSPy model with chatgpt-4o-mini
    lm = dspy.LM('openai/gpt-4o-mini', max_tokens=5000)
    dspy.configure(lm=lm)

    # Run the prompt through the model
    module = dspy.Predict(ExtractData)
    
    response = module(text=prompt, textual_data=markdown_content)

    # Convert response to JSON format
    json_output = response.json_output
    
    try:
        json_data = json.loads(response.json_output)
    except json.JSONDecodeError:
        print("Error: The response is not valid JSON.")
        return None

    # Save the output to a JSON file
    try:
        with open(output_json_file, 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, indent=4)
        print(f"Output successfully saved to '{output_json_file}'")
    except Exception as e:
        print(f"Error writing to JSON file: {e}")

# ============
# Main Code
# ============

# markdown_file_path = "./data_markdown/8.md"
# output_json_file = "./data_json/8.json"
prompt = '''
Please categorize the relevant paragraphs from the unstructured text data into the provided JSON template without altering the content. Ensure accuracy and completeness based on the original document.

JSON Template:
{
    "case_title": "",
    "case_number": "",
    "case_details": {
        "introduction": "<related_paragraphs>",
        "applicable_laws_and_procedural_rules": "<related_paragraphs>",
        "methodology": "<related_paragraphs>",
        "background_information": "<related_paragraphs>",
        "investigation_details": "<related_paragraphs>",
        "conclusions": "<related_paragraphs>",
        "recommendations": "<related_paragraphs>",
        "others": "<related_paragraphs>",
    }
}
'''
for i in range(0, 74):
    markdown_file_path = f"./data_markdown/{i}.md"
    output_json_file = f"./data_json_updated_2/{i}.json"
    if os.path.isfile(markdown_file_path):
        process_markdown_with_dspy(markdown_file_path, output_json_file, prompt)
        print(f"Converted {i}.md to JSON")
    else:
        print(f"Skipped number {i}")

