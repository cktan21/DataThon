import json
import spacy
import pandas as pd
import os
    
nlp = spacy.load("en_core_web_sm")

def normalize_text(text):
    doc = nlp(text)
    normalized_tokens = []
    for token in doc:
        # Remove stop words, punctuation, and whitespace
        if not token.is_stop and not token.is_punct and not token.is_space:
            # Lemmatize and lowercase
            normalized_tokens.append(token.lemma_.lower())
    return " ".join(normalized_tokens)

sections = ["introduction", "investigation_details", "applicable_laws_and_procedural_rules", "methodology", "background_information", "conclusions", "recommendations", "others"]

for i in range(0, 74):
    input_file_path = f"./data_json_updated_2/{i}.json"
    output_json_file = f"./data_json_normalized/{i}.json"
    if os.path.isfile(input_file_path):
        with open(input_file_path, "r") as f:
            data = json.load(f)

        # Normalize text for each specified section
        normalized_case_details = {}
        for section in sections:
            # Get the section text; if the section is missing, use an empty string.
            section_text = data.get("case_details", {}).get(section, "")
            normalized_case_details[section] = normalize_text(section_text)

        # Build the final JSON structure
        output_data = {
            "case_title": data.get("case_title", ""),  # Use empty string if case_title is not present
            "case_number": data.get("case_number", ""),
            "case_details": normalized_case_details
        }

        # Write the normalized data to a new JSON file
        with open(output_json_file, "w") as outfile:
            json.dump(output_data, outfile, indent=4)

        print("Normalized JSON has been written to normalized.json")


# df = pd.DataFrame({
#     "case_number": [data["case_number"]],  # Wrap in a list
#     "normalized_text": [normalized_corpus]  # Wrap in a list
# }, index=[0])  # Explicit index

# df.to_csv('normalized.csv', index=False)