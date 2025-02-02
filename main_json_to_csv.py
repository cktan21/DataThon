import json
import glob
import pandas as pd

# Define the input directory containing your JSON files and the output CSV filenames
input_dir = './data_json_entity_relationships/'  # Directory with JSON files
entities_csv_file = 'entities.csv'
relationships_csv_file = 'relationships.csv'

# Use glob to find all JSON files in the input directory
json_files = glob.glob(f"{input_dir}*.json")

# Prepare lists to store rows for entities and relationships
entity_rows = []
relationship_rows = []

# Loop through each JSON file found in the directory
for json_file in json_files:
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Retrieve the top-level case info
    case_title = data.get("case_title", "")
    case_number = data.get("case_number", "")
    case_details = data.get("case_details", {})

    # Iterate through each section under case_details
    for section, details in case_details.items():
        # Process entities
        entities = details.get("entities", [])
        for ent in entities:
            entity_rows.append({
                "case_title": case_title,
                "case_number": case_number,
                "section": section,
                "entity_text": ent.get("text", ""),
                "entity_label": ent.get("label", "")
            })

        # Process relationships
        relationships = details.get("relationships", [])
        for rel in relationships:
            relationship_rows.append({
                "case_title": case_title,
                "case_number": case_number,
                "section": section,
                "source": rel.get("source", ""),
                "target": rel.get("target", ""),
                "relationship": rel.get("relationship", "")
            })

# Convert the lists into DataFrames
df_entities = pd.DataFrame(entity_rows)
df_relationships = pd.DataFrame(relationship_rows)

# Write the DataFrames to CSV files
df_entities.to_csv(entities_csv_file, index=False, encoding='utf-8')
df_relationships.to_csv(relationships_csv_file, index=False, encoding='utf-8')

print(f"Entities CSV file created: {entities_csv_file}")
print(f"Relationships CSV file created: {relationships_csv_file}")
