import json
import dspy
import os

# Define the DSPy signature for relationship extraction.
class ExtractEntityRelations(dspy.Signature):
    text: str = dspy.InputField()
    entity_data: str = dspy.InputField(desc="JSON list of entities")
    context: str = dspy.InputField(desc="context window for entities")
    json_output: str = dspy.OutputField(desc="Entity relationship JSON output")

def process_entity_relationships(entity_data, context, prompt):
    """
    Given a JSON string of entities and a prompt, use the DSPy model
    to extract relationships between the entities.
    Returns the parsed JSON output containing relationships.
    """
    # Initialize the DSPy model (using chatgpt-4o-mini, for example)
    lm = dspy.LM('openai/gpt-4o-mini', max_tokens=10000)
    dspy.configure(lm=lm)

    # Run the prompt through the model
    module = dspy.Predict(ExtractEntityRelations)
    response = module(text=prompt, context=context, entity_data=entity_data)
    
    json_output = response.json_output
    print("Raw relationship output:", json_output)
    
    try:
        json_data = json.loads(json_output)
    except json.JSONDecodeError:
        print("Error: Relationship extraction response is not valid JSON.")
        json_data = {"relationships": []}
    
    return json_data

# Relationship extraction prompt
relationship_prompt = '''
Given the following list of entities (in JSON format), extract any relationships between them.
For each relationship, create an object with the following keys:
- "source": the first entity involved
- "target": the second entity involved
- "relationship": a description of the relationship between them

Return the results in JSON format as follows:
{
    "relationships": [
        {"source": "<entity_text1>", "target": "<entity_text2>", "relationship": "<relationship_type>"},
        {"source": "<entity_text3>", "target": "<entity_text4>", "relationship": "<relationship_type>"}
    ]
}
If no relationships can be determined, return an empty array for "relationships".
Respond with JSON only, without any additional text, code block markers, or explanations.
'''

for i in range(0, 74):
    # File paths
    input_json_file = f"./data_json_entity/{i}.json"  # your file with entities (example name)
    normalized_json_file = f"./data_json_normalized/{i}.json"
    output_json_file = f"./data_json_entity_relationships/{i}.json"

    if os.path.isfile(input_json_file) and os.path.isfile(normalized_json_file):
        # Load the existing JSON that contains the entities for each section.
        with open(input_json_file, "r", encoding="utf-8") as f:
            input_data = json.load(f)
            
        with open(normalized_json_file, "r", encoding="utf-8") as g:
            normalized_data = json.load(g)

        # List of sections (make sure these match your JSON structure)
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

        # Process each section for relationship extraction
        for section in sections:
            section_entities = input_data.get("case_details", {}).get(section, {})
            # Ensure the section contains an "entities" key.
            if section_entities and "entities" in section_entities:
                # Convert the entity data to a JSON string
                entities_json_str = json.dumps(section_entities)
                
                section_normalized_text = normalized_data.get("case_details", {}).get(section, {})
                
                # Extract relationships using the DSPy function
                relationships_data = process_entity_relationships(entities_json_str, section_normalized_text, relationship_prompt)
                # Add the relationships to the section data
                input_data["case_details"][section]["relationships"] = relationships_data.get("relationships", [])
            else:
                # If no entities are found, just add an empty relationships list.
                input_data["case_details"][section] = {"entities": [], "relationships": []}

        # Save the final JSON with relationships added
        with open(output_json_file, "w", encoding="utf-8") as outfile:
            json.dump(input_data, outfile, indent=4)

        print(f"Entity relationship extraction completed. Output saved to '{output_json_file}'.")
    else:
        print(f"Invalid file found, skipping {i}")
