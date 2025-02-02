import pymupdf
import os
import spacy
nlp = spacy.load("en_core_web_sm")

doc1 = r"C:\Users\bonbo\Desktop\SMU\Datathon\pdfs\4.pdf"


def analyze_doc(doc):
    datas = get_data(doc)

    results = [extract_entities(datas), extract_relationships(datas)]
    
    return results

def get_data(doc):
    full_doc = []
    delimiter = " "
    if not validate_pdf(doc):
        raise ValueError("File format error: The file is not a PDF.")
    else:
         doc = pymupdf.open(doc)
    for page in doc:
            text = page.get_text()
            full_doc.append(text)
    
    cleanned_doc = delimiter.join(full_doc)
    return cleanned_doc

def validate_pdf(doc):
    if not doc.lower().endswith('.pdf'):
        return False
    return True

def extract_entities(text):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

def extract_relationships(text):
    doc = nlp(text)
    relationships = []
    
    for token in doc:
        if token.dep_ == "ROOT":  # Main verb
            subject = [w.text for w in token.lefts if w.dep_ in ("nsubj", "nsubjpass")]
            objects = [w.text for w in token.rights if w.dep_ in ("dobj", "pobj")]
            
            if subject and objects:
                relationships.append((subject[0], token.text, objects[0]))
    
    return relationships


test = """Pristina Airport – Possible administrative irregularity regarding tender procedures involving Vendor 1 and Vendor 2

Allegation

Two companies with the same owner took part at least three times in the same Airport tenders.

Background Information

The Kosovo citizen, Vendor 1 and Vendor 2 Representative, is the owner and Director of the Pristina-based Vendor 1 and also a 51% shareholder of the Pristina-Ljubljana-based company Vendor 2. Both companies have their residences at the same address in Pristina.

Both Vendor 1 and Vendor 2 submitted three times in 2003 for the same tenders:

Supply and Mounting of Sonic System in the Fire Station Building. Winner was Vendor 2 with €1,530 followed by Vendor 1 with €1,620. The third company, Vendor 3, did not provide a price offer.

Cabling of Flat Display Information System (FIDS). Winner was Vendor 1 with €15,919 followed by Vendor 2 with €19,248.70. The other two competitors, Vendor 3 and Vendor 4, offered prices of Euro 19,702 and Euro 21,045.

Purchase and fixing of Cramer Antenna. Winner was again Vendor 1 with €3,627.99 followed by Vendor 2 with €3,921. The other two competitors, Vendor 3 and Vendor 4, offered prices of €4,278 and €4,670."""

# print(analyze_doc(doc1))
print(extract_relationships(test))