import json
import pandas as pd
import spacy
from collections import Counter
import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt
nlp = spacy.load("en_core_web_lg")


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


# instance = Data(data['case_number'], data['case_title'], data['case_details'])

# details = instance.detail
for i in range(1, 35):
    with open(f'{i}.json', 'r') as file:
        holder.append(json.load(file))




df_clean = pd.json_normalize(holder)

df_clean.columns = ['Number', 'Title', 'Introduction', 'Applicable Laws & Procedural Rules', 'Methodology', 'Background Info', 'Investigation Details', 'Conclusions', 'Recommendations', 'Others']


# for listies in df_clean['Introduction']:
#     for chunks in listies:
#         if 
    

df_clean = pd.json_normalize(holder)
df_clean.columns = ['Number', 'Title', 'Introduction', 'Applicable Laws & Procedural Rules', 'Methodology', 'Background Info', 'Investigation Details', 'Conclusions', 'Recommendations', 'Others']

# Combine columns for each row into a single string
documents = df_clean.apply(lambda row: ' '.join(row.astype(str)), axis=1).tolist()

# Create the Bag-of-Words representation
# vectorizer = CountVectorizer(ngram_range=(2,2))
# matrix = vectorizer.fit_transform(documents)  # Fit on the list of row strings
# bow_df = pd.DataFrame(matrix.toarray(), columns=vectorizer.get_feature_names_out())

# # Print the Bag-of-Words DataFrame
# print(bow_df)

# Tokenize documents and remove stopwords
def preprocess(doc):
    return [token.text.lower() for token in nlp(doc) if not token.is_stop and token.is_alpha]

# Preprocess all documents
processed_docs = [preprocess(doc) for doc in documents]

# Find common words across all documents
word_counts = Counter()
for doc in processed_docs:
    word_counts.update(set(doc))  # Count unique words in each document

# Identify words that appear in all documents
common_words = {word for word, count in word_counts.items() if count == len(processed_docs)}

# Filter out common words from each document
filtered_docs = []
for doc in processed_docs:
    filtered_doc = [word for word in doc if word not in common_words]
    filtered_docs.append(' '.join(filtered_doc))  # Convert back to a single string

# Convert filtered documents to spaCy Doc objects (for word vectors)
docs = [nlp(doc) for doc in filtered_docs]

# Compute cosine similarity between each pair of rows
similarity_matrix = []
for doc1 in docs:
    row = []
    for doc2 in docs:
        # Compute cosine similarity between two document vectors
        similarity = doc1.similarity(doc2)
        row.append(similarity)
    similarity_matrix.append(row)

# Convert the similarity matrix to a DataFrame for better visualization
similarity_df = pd.DataFrame(similarity_matrix, index=df_clean['Number'], columns=df_clean['Number'])

# # Print the similarity matrix
# print("Cosine Similarity Matrix:")
# print(similarity_df)


# Below is network graph


# # Create a graph from the similarity matrix
# G = nx.Graph()

# # Add nodes (documents) to the graph
# for doc_id in df_clean['Number']:
#     G.add_node(doc_id, title=df_clean[df_clean['Number'] == doc_id]['Title'].values[0])

# # Add edges (similarity scores) to the graph
# threshold = 0.5  # Set a threshold for similarity to include edges
# for i in range(len(similarity_df)):
#     for j in range(i + 1, len(similarity_df)):
#         if similarity_df.iloc[i, j] > threshold:
#             G.add_edge(similarity_df.index[i], similarity_df.columns[j], weight=similarity_df.iloc[i, j])

# # Visualize the graph
# plt.figure(figsize=(12, 8))
# pos = nx.spring_layout(G, seed=42)  # Layout for positioning nodes
# nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue')
# nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
# nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')

# # Add edge labels (similarity scores)
# edge_labels = {(u, v): f"{d['weight']:.2f}" for u, v, d in G.edges(data=True)}
# nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

# plt.title("Document Similarity Network", fontsize=16)
# plt.axis('off')  # Turn off the axis
# plt.show()

# # # Analyze the network
# # print("Number of nodes:", G.number_of_nodes())
# # print("Number of edges:", G.number_of_edges())
# # print("Average degree:", sum(dict(G.degree()).values()) / G.number_of_nodes())

# # # Centrality measures
# # degree_centrality = nx.degree_centrality(G)
# # betweenness_centrality = nx.betweenness_centrality(G)
# # closeness_centrality = nx.closeness_centrality(G)

# # # Print centrality measures for each node
# # print("\nDegree Centrality:")
# # for node, centrality in degree_centrality.items():
# #     print(f"Node {node}: {centrality:.4f}")

# # print("\nBetweenness Centrality:")
# # for node, centrality in betweenness_centrality.items():
# #     print(f"Node {node}: {centrality:.4f}")

# # print("\nCloseness Centrality:")
# # for node, centrality in closeness_centrality.items():
# #     print(f"Node {node}: {centrality:.4f}")

# Create a graph from the similarity matrix
G = nx.Graph()

# Add nodes (documents) to the graph
for doc_id in df_clean['Number']:
    G.add_node(doc_id, title=df_clean[df_clean['Number'] == doc_id]['Title'].values[0])

# Add edges (similarity scores) to the graph
threshold = 0.95  # Set a threshold for similarity to include edges
for i in range(len(similarity_df)):
    for j in range(i + 1, len(similarity_df)):
        if similarity_df.iloc[i, j] > threshold:
            G.add_edge(similarity_df.index[i], similarity_df.columns[j], weight=similarity_df.iloc[i, j])

# Create a PyVis network
net = Network(notebook=True, height="750px", width="100%", bgcolor="#222222", font_color="white")

# Add nodes and edges to the PyVis network
for node, node_attrs in G.nodes(data=True):
    net.add_node(node, title=node_attrs['title'], label=str(node))

for u, v, edge_attrs in G.edges(data=True):
    net.add_edge(u, v, value=edge_attrs['weight'], title=f"Similarity: {edge_attrs['weight']:.2f}")

# Customize the network
net.toggle_physics(True)  # Enable physics for better layout
net.show_buttons(filter_=['physics'])  # Show configuration buttons

# Save the network to an HTML file
net.show("network.html")

print("Network saved to network.html. Open this file in a web browser to view the interactive network.")