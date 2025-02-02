import json
import pandas as pd
import spacy
from collections import defaultdict

# Load spaCy's pre-trained model
nlp = spacy.load("en_core_web_lg")

# Set Pandas display options
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_colwidth', 10000)
pd.set_option('display.width', 120)
pd.set_option('expand_frame_repr', True)

class Data:
    def __init__(self, no, title, detail):
        self.no = no
        self.title = title
        self.detail = detail

holder = []

# Load JSON files
for i in range(1, 35):
    with open(f'{i}.json', 'r') as file:
        holder.append(json.load(file))

# Normalize JSON data into a DataFrame
df_clean = pd.json_normalize(holder)
df_clean.columns = ['Number', 'Title', 'Introduction', 'Applicable Laws & Procedural Rules', 
                    'Methodology', 'Background Info', 'Investigation Details', 'Conclusions', 
                    'Recommendations', 'Others']

# Combine columns for each row into a single string
documents = df_clean.apply(lambda row: ' '.join(row.astype(str)), axis=1).tolist()

# Function to extract entities
def extract_entities(text):
    """Extract named entities and their types using spaCy"""
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

# Function to extract relationships with increased context
def extract_relationships(text):
    """Extract relationships between entities with expanded context"""
    doc = nlp(text)
    relationships = []
    
    for sent in doc.sents:
        for token in sent:
            if token.dep_ == "ROOT":  # Main verb
                # Expand context window around the ROOT token
                start = max(0, token.i - 10)  # 10 tokens before the ROOT
                end = min(len(sent), token.i + 11)  # 10 tokens after the ROOT
                context = sent[start:end].text  # Extract the context window
                
                # Extract subject and object
                subject = [w.text for w in token.lefts if w.dep_ in ("nsubj", "nsubjpass")]
                objects = [w.text for w in token.rights if w.dep_ in ("dobj", "pobj")]
                
                if subject and objects:
                    relationships.append({
                        "subject": subject[0],
                        "verb": token.text,
                        "object": objects[0],
                        "context": context
                    })
    
    return relationships

# Track entities and relationships across all files
all_entities = defaultdict(set)  # {file_number: set of entities}
all_relationships = defaultdict(list)  # {file_number: list of relationships}
cross_file_relationships = defaultdict(list)  # {entity: list of related entities across files}

# Process each document
for idx, (doc_text, file_number) in enumerate(zip(documents, df_clean['Number'])):
    # Extract entities
    entities = extract_entities(doc_text)
    all_entities[file_number].update(entities)
    
    # Extract relationships within the file
    relationships = extract_relationships(doc_text)
    all_relationships[file_number].extend(relationships)
    
    # Track relationships across files
    for rel in relationships:
        cross_file_relationships[rel["subject"]].append((file_number, rel["object"]))
        cross_file_relationships[rel["object"]].append((file_number, rel["subject"]))

# Prepare output data
output_data = {
    "files": {},
    "cross_file_relationships": []
}

# Add entities and relationships for each file
for file_number in all_entities:
    output_data["files"][file_number] = {
        "entities": [{"text": ent, "label": label} for ent, label in all_entities[file_number]],
        "relationships": all_relationships[file_number]
    }

# Add cross-file relationships
for entity, related_entities in cross_file_relationships.items():
    output_data["cross_file_relationships"].append({
        "entity": entity,
        "related_entities": [{"file": file_num, "related_entity": rel_ent} for file_num, rel_ent in related_entities]
    })

# Save output to a JSON file
with open("output.json", "w") as f:
    json.dump(output_data, f, indent=4)

print("Output saved to output.json")