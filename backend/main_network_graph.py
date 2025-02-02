import json
import networkx as nx
import matplotlib.pyplot as plt

# Load the JSON data from file (update the path as needed)
with open('data_json_entity_relationships/8.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create a directed graph (you can also use nx.Graph() for undirected graphs)
G = nx.DiGraph()

# Loop through each section in "case_details"
case_details = data.get("case_details", {})
for section, content in case_details.items():
    # Get entities and relationships for the current section
    entities = content.get("entities", [])
    relationships = content.get("relationships", [])
    
    # Add each entity as a node (if not already present)
    for entity in entities:
        entity_text = entity.get("text")
        entity_label = entity.get("label")
        if entity_text not in G.nodes:
            G.add_node(entity_text, label=entity_label)
    
    # Add each relationship as a directed edge
    for rel in relationships:
        source = rel.get("source")
        target = rel.get("target")
        rel_type = rel.get("relationship")
        # Optionally, if nodes are not already added from the entities list,
        # you can add them here as well.
        if source not in G.nodes:
            G.add_node(source, label="Unknown")
        if target not in G.nodes:
            G.add_node(target, label="Unknown")
        # Add the edge with an attribute for the relationship type.
        G.add_edge(source, target, relationship=rel_type)

# Set up the layout for the nodes in the graph
pos = nx.spring_layout(G, k=0.5, seed=42)  # adjust k for spacing

# Create a figure for the network graph
plt.figure(figsize=(14, 10))

# Draw nodes with a specified size and color
nx.draw_networkx_nodes(G, pos, node_size=1500, node_color="skyblue", alpha=0.9)

# Create node labels that include the entity text and its type
node_labels = {node: f"{node}\n({G.nodes[node].get('label', '')})" for node in G.nodes()}
nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10)

# Draw the edges with arrows
nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle='->', arrowsize=20)

# Create edge labels using the "relationship" attribute on each edge
edge_labels = {(u, v): d.get("relationship", "") for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=9)

# Add a title and turn off the axis
plt.title(f"Entity Relationship Graph:\n{data.get('case_title', '')}", fontsize=16)
plt.axis("off")
plt.tight_layout()

# Display the graph
plt.show()
