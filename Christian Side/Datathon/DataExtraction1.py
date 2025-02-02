import pymupdf
import os
import json
import pandas as pd
import spacy
nlp = spacy.load("en_core_web_lg")

from sklearn.feature_extraction.text import CountVectorizer

document = r"C:\Users\bonbo\Desktop\SMU\Datathon\data_json\1.json"

df = pd.read_json(document)

df_string = df.to_string()

vectorizer = CountVectorizer()

matrix = vectorizer.fit_transform(df_string)

bow_df = pd.DataFrame(matrix.toarray())

# Map the column names to vocabulary 
bow_df.columns = vectorizer.get_feature_names()

# Print bow_df
print(bow_df)