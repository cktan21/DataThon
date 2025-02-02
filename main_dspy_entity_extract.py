import dspy
import json
import os

# Define the DSPy signature
class ExtractData(dspy.Signature):
    text: str = dspy.InputField()
    textual_data: str = dspy.InputField(desc="Normalized text data")
    json_output: str = dspy.OutputField(desc="Respond with JSON only, without any additional text, code block markers, or explanations.")

def process_normalized_text_dspy(normalized_text, prompt):
    """
    Process the normalized text through the DSPy model using the given prompt.
    Returns the parsed JSON output containing named entities.
    """
    # Initialize the DSPy model with chatgpt-4o-mini
    lm = dspy.LM('openai/gpt-4o-mini', max_tokens=10000)
    dspy.configure(lm=lm)

    # Run the prompt through the model
    module = dspy.Predict(ExtractData)
    response = module(text=prompt, textual_data=normalized_text)

    json_output = response.json_output
    print("Raw JSON output for section:", json_output)

    try:
        json_data = json.loads(json_output)
    except json.JSONDecodeError:
        print("Error: The response is not valid JSON for the provided text.")
        json_data = {"entities": []}  # Return an empty structure if JSON decoding fails

    return json_data

# ============
# Main Code
# ============

# The prompt instructing the model what to do
prompt = '''
Extract all named entities from the following normalized text and label the entity based on their entity type. Return the output in JSON format as shown:
JSON Template:
{
    "entities": [
        {"text": "<entity_text1>", "label": "<entity_type1>" },
        {"text": "<entity_text2>", "label": "<entity_type2>" }
    ]
}
'''

# Define the sections to process
sections = [
    "introduction",
    "investigation_details",
    "applicable_laws_and_procedural_rules",
    "methodology",
    "background_information",
    "conclusions",
    "recommendations",
    "others"
]

# Loop through the JSON files (assuming they are numbered 0 to 73)
for i in range(0, 74):
    input_file_path = f"./data_json_normalized/{i}.json"
    output_json_file = f"./data_json_entity/{i}.json"

    if os.path.isfile(input_file_path):
        with open(input_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Dictionary to hold the entity extraction for each section
        entities_output = {}

        for section in sections:
            # Get the text for the section; if missing, use an empty string
            section_text = data.get("case_details", {}).get(section, "")
            if section_text.strip():
                extracted_entities = process_normalized_text_dspy(section_text, prompt)
            else:
                extracted_entities = {"entities": []}  # If no text is available, return empty entities

            entities_output[section] = extracted_entities

        # Build the final JSON structure
        output_data = {
            "case_title": data.get("case_title", ""),
            "case_number": data.get("case_number", ""),
            "case_details": entities_output
        }

        # Write the final JSON output to a file
        try:
            with open(output_json_file, 'w', encoding='utf-8') as json_file:
                json.dump(output_data, json_file, indent=4)
            print(f"Output successfully saved to '{output_json_file}'")
        except Exception as e:
            print(f"Error writing to JSON file '{output_json_file}': {e}")
