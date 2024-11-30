import os
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from networkx.algorithms import isomorphism
from networkx.algorithms import similarity
import networkx as nx
import matplotlib.pyplot as plt
import grakel as gk

load_dotenv()

client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'),)

META_PROMPT = '''

'''

class AnalogyFormat(BaseModel):
    concept: str
    summary: str
    knowledge_graph: str
    analogies: str
    
class GeneratedAnalogyFormat(BaseModel):
    AnalogyNumber: int
    Analogies : list[str]
    Filtered_Analogies: list[str]
    KnowledgeGraph1: str
    KnowledgeGraph2: str
    KnowledgeGraph3: str
    

def get_response(prompt):
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a very knowledge assistant who have comprehensive knowledge in Analogy and Cognitive Science, as well as Computer Science. You have read Gentner's Structure Mapping theory and Hofstadter's Analogy theory very well and is a master in this field. "},
            {"role": "user", "content": prompt},
        ],
    )
    return chat_completion

def generate_kg(prompt):
    prompt = f"""
    Generate a comprehensive knowledge summary for the concept: {prompt}
    Provide the knowledge graph in the form of triplets (entity, relation, entity) based on the summary.
    This Knowledge Graph should have a comprehensive structure where most of the nodes are connected together naturally.
    Each triplet will be separated by a new line."""
    chat_completion = client.beta.chat.completions.parse(
        model = "gpt-4o",
        messages = [
            {"role": "system", "content": "You are a very knowledge assistant who have comprehensive knowledge in Analogy and Cognitive Science, as well as Computer Science. You have read Gentner's Structure Mapping theory and Hofstadter's Analogy theory very well and is a master in this field. "},
            {"role": "user", "content": prompt},
        ],
        response_format=AnalogyFormat
    )
    return chat_completion.choices[0].message.parsed
    
    #return get_response(prompt)

def generate_analogy(prompt):
    prompt1 = f"""
    I want you to be an analogy expert that can take one concept, understand the concept and its internal structure clearly, and give several analogies that can help others better understand it. You can take this step-by-step approach for analogy generation:
    1. When giving a concept, generate a comprehensive summary of the concept;
    2. Based on the concept, generate a knowledge graph with the entities and relations extracted from the concept;
    3. First generate 10 analogies based on your understanding, from different areas, including computer, philosophy, biology, and more.
    4. Filter and find 3 analogies that has the most similar structure as the given concept and semantically different from each other, and form 3 knowledge graphs of their own. 
    5. Each Knowledge graph should have a comprehensive and standalone structure not related to the original concept, formatted in the form of triplets (entity, relation, entity), and separated by a new line.
    """
    chat_completion = client.beta.chat.completions.parse(
        model = "gpt-4o",
        messages = [
            {"role": "system", "content": "You are a very knowledge assistant who have comprehensive knowledge in Analogy and Cognitive Science, as well as Computer Science. You have read Gentner's Structure Mapping theory and Hofstadter's Analogy theory very well and is a master in this field. You are here to help generate analogies for the given concept."},
            {"role": "user", "content": prompt},
            {"role": "user", "content": prompt1},
        ],
        response_format=GeneratedAnalogyFormat
    )
    return chat_completion.choices[0].message.parsed

def draw_kg(kg, ax=None):
    G = nx.DiGraph()
    for triplet in kg.split('\n'):
        try:
            entity1, relation, entity2 = triplet.strip().split(',')
            G.add_edge(entity1.strip(), entity2.strip(), label=relation.strip())
        except ValueError as e:
            print(f"Skipping invalid triplet: {triplet}, error: {e}")

    pos = nx.spring_layout(G, seed=1)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=1000, node_color='skyblue', alpha=0.9, label=True)
    nx.draw_networkx_edges(G, pos, ax=ax, arrowstyle="->", arrowsize=20, edge_color="black")
    
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax, font_size=8, font_color="black", font_weight="bold")
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_color="black", font_weight="bold")
    if ax!= None : ax.set_title("Knowledge Graph", fontsize=10)
    return G
    
def draw_kg_list(kgs):
    num_kgs = len(kgs)
    fig, axes = plt.subplots(1, num_kgs, figsize=(5*num_kgs, 5))
    if num_kgs == 1:
        axes = [axes]  # Wrap in a list for single subplot
    for i, (kg, ax) in enumerate(zip(kgs, axes), 1):
        draw_kg(kg, ax=ax)
        ax.set_title(f"Graph {i}", fontsize=10)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    concept = "Filter Bubble in AI Recommendation System"
    #get_response()
    event = generate_kg(concept)
    print(event)
    nxg = draw_kg(event.knowledge_graph)
    
    
    # kernel = gk.graph_from_networkx(nxg)
    # gk.GraphKernel("random_walk", with_labels=True).fit_transform([kernel])
    #plt.tight_layout()
    #plt.show()
    
    analogies_kg = generate_analogy(event.summary)
    nxg1 = draw_kg(analogies_kg.KnowledgeGraph1)
    nxg2 = draw_kg(analogies_kg.KnowledgeGraph2)
    nxg3 = draw_kg(analogies_kg.KnowledgeGraph3)
    for v in similarity.optimize_graph_edit_distance(nxg, nxg1):
        minv = v
    print(minv)
    #print(analogies_kg)
    #draw_kg_list([analogies_kg.KnowledgeGraph1, analogies_kg.KnowledgeGraph2, analogies_kg.KnowledgeGraph3])













# def draw_kg_list(kgs):
#      fig, axes = plt.subplots(2,2)
#      for i, kg in enumerate(kgs, 1):
#         print(f"Drawing Graph {i}")
#         G = nx.DiGraph()
#         for triplet in kg.split('\n'):
#             try:
#                 entity1, relation, entity2 = triplet.strip().split(',')
#                 G.add_edge(entity1.strip(), entity2.strip(), label=relation.strip())
#             except ValueError:
#                 print(f"Skipping invalid triplet: {triplet}")
#         pos = nx.spring_layout(G)
#         edge_labels = nx.get_edge_attributes(G, 'label')
#         nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
#         nx.draw(G, pos, with_labels=True, node_size=1000, node_color="skyblue", font_size=5, font_weight="bold", font_color="black", edge_color="black", linewidths=1, arrowsize=20)
#         plt.title(f"Knowledge Graph {i}")
#         plt.show()
        
# def draw_multi_kg(kg):
#     G = nx.MultiDiGraph()
#     for triplet in kg.split('\n'):
#         try:
#             entity1, relation, entity2 = triplet.strip().split(',')
#             G.add_edge(entity1.strip(), entity2.strip(), label=relation.strip())
#         except ValueError as e:
#             print(f"Skipping invalid triplet: {triplet}, error: {e}")

#     pos = nx.spring_layout(G)

#     # Draw nodes
#     nx.draw_networkx_nodes(G, pos, node_size=1000, node_color='skyblue', label=True)

#     # Draw edges
#     nx.draw_networkx_edges(G, pos, edgelist=G.edges(), arrowstyle="->", arrowsize=20, edge_color="black")

#     # Draw labels
#     edge_labels = nx.get_edge_attributes(G, 'label')
#     nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
#     nx.draw_networkx_labels(G, pos, font_size=8, font_color="black", font_weight="bold")

#     plt.title("Knowledge Graph")
#     plt.show()
    
# def draw_multi_kg_list(kgs):
#     for i, kg in enumerate(kgs, 1):
#         print(f"Drawing Graph {i}")
#         draw_multi_kg(kg)