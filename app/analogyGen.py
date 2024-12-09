import os
from openai import OpenAI
#from dotenv import load_dotenv
from pydantic import BaseModel
import networkx as nx
from networkx.algorithms import isomorphism
from networkx.algorithms import similarity
import matplotlib.pyplot as plt
import prompts
import base64
import textwrap
import utils
import cluster

#load_dotenv()

client = OpenAI(api_key = utils.OPENAI_API_KEY)

General_Msg = []
Analogy_KG = ""
Relation_Set = ""
Analogy_KGs= []
class KGFormat(BaseModel):
    concept: str
    tentative_summaries : list[str]
    summary: str
    knowledge_graph: str
    relation_set: str
    
class AnalogyFormat(BaseModel):
    Analogies : list[str]
    Analogies_KnowledgeGraphs: list[str]
    
class CoreConcepts(BaseModel):
    core_concepts: list[str]
    
class FilteredAnalogyFormat(BaseModel):
    Filtered_Analogies: list[str]
    Filtered_Analogies_Explanation: list[str]
    Filtered_Analogies_Terminology: list[str]
    Filtered_Analogies_KnowledgeGraphs: list[str]
    
class FilteredAnalogy(BaseModel):
    concept: list[str]
    summary: list[str]
    terminology: list[str]
    
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_image
    
def add_image(image, role, messages, message):
    General_Msg.append({"role": role, "content": [
        {"type": "text", "text": message},
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{image}"
            }
        }
    ]})
    return General_Msg
    
def add_message(message, role, messages=None):
    General_Msg.append({"role": role, "content": message})
    return General_Msg

def send_message(model, messages):
    content = client.chat.completions.create(model=model, messages=messages, temperature=0.2)
    General_Msg.append({"role": "system", "content": content.choices[0].message.content})
    #messages.clear()
    return content

def parse_message(model, messages, format):
    content = client.beta.chat.completions.parse(model=model, messages=messages, response_format=format, temperature=0.2)
    General_Msg.append({"role": "system", "content": content.choices[0].message.content})
    #messages.clear()
    return content

def generate_core_meanings(concept):
    prompt1 = f"""Based on the concept and the previous generated summary, generate the core meanings revolving around the concept: {concept}. For example, with the filter bubble concept, the core meaningful extracted should be "Limited Exposure to Diverse World", "Lack of Transparency", and "Social Media Landscape". Make sure these core meanings are generalizable beyond the summary itself and are the core concepts that are essential to understand the concept. Put the core concepts in the "core_concepts" field."""
    prompt1 = textwrap.dedent(prompt1).strip()
    messages = add_message(prompt1, "system", [])
    result = parse_message("gpt-4o", messages, CoreConcepts)
    return result.choices[0].message.parsed.core_concepts
    

def generate_summary(concept):
    prompt1 = f"""Generate ten tentative knowledge summaries for the concept: {concept} and put the tentative summaries in the "tentative_summaries" field.. After the generation, summarize all the tentative summaries and put it in the "summary" field. """
    prompt1 = textwrap.dedent(prompt1).strip()
    messages = add_message(prompt1, "user", [])
    res = send_message("gpt-4o", messages).choices[0].message.content
    add_message(res, "user")
    return res
    
    
def generate_kg(prompt):
    
    prompt2 = """Provide the knowledge graph for the concept in the form of triplets `entity, relation, entity` based on the previous summary. Focus on the core concepts that is generalizable beyond the summary itself (e.g., terms, events, interactions, theories) and the relationships between these concepts. My job depends on your ability to generate a comprehensive yet concentrated knowledge graph in which each node's out degree is at least three. If I cannot deliver to my boss a high-quality knowledge that they will make a layman fully comprehend the summarized subject itself, I WILL LOSS MY JOB.
This Knowledge Graph should have a comprehensive structure where most of the nodes are connected together naturally.
Each triplet will be separated by a new line."""

    prompt3 = """Given the triplets, aggregate the similar concepts under one concept name, and replace all the similar concepts name with that one concept name. Prune the trivial entities and relations that do not have strong relation with the concept's deep meaning. Return a revised triplets in the form of triplets `entity, relation, entity`, with each separated by a new line. After that, return all the relation sets in the triplet and put it in the "relation_set" field."""
    
    prompt2 = textwrap.dedent(prompt2).strip()
    prompt3 = textwrap.dedent(prompt3).strip()
    
    #need to chain previous result
    
    #full_prompt = f"{prompt2}\n\nPrevious Output: {prev_content}"
    #messages = add_message(full_prompt, "user", [])
    messages = add_message(prompt2, "user")
    prev_content = send_message("gpt-4o", messages).choices[0].message.content
    add_message(prev_content, "user")
    
    # full_prompt = f"{prompt3}\n\nPrevious Output: {prev_content}"
    # messages = add_message(prompt3, "user", messages)
    messages = add_message(prompt3, "user")
    result = parse_message("gpt-4o", messages, KGFormat)
    
    return result.choices[0].message.parsed

def generate_analogy_kg(prompt):
    #Generate knwoledge graphs
    prompt1 = f"""Generate a comprehensive knowledge summary for the concept: {prompt}"""
    
    prompt2 = """Provide the knowledge graph for the concept in the form of triplets `entity, relation, entity` based on the previous summary. Focus on the core concepts that is generalizable beyond the summary itself (e.g., terms, events, interactions, theories) and the relationships between these concepts. My job depends on your ability to generate a comprehensive yet concentrated knowledge graph in which each node's out degree is at least three. If I cannot deliver to my boss a high-quality knowledge that they will make a layman fully comprehend the summarized subject itself, I WILL LOSS MY JOB.
This Knowledge Graph should have a comprehensive structure where most of the nodes are connected together naturally.
Each triplet will be separated by a new line."""

    prompt3 = """Given the triplets, aggregate the similar concepts under one concept name, and replace all the similar concepts name with that one concept name. Prune the trivial entities and relations that do not have strong relation with the concept's deep meaning. Return a revised triplets in the form of triplets `entity, relation, entity`, with each separated by a new line. Follow the Given Relation Set to prune the trivial entities and relations and keep a more deep relationship graph."""
    
    prompt1 = textwrap.dedent(prompt1).strip()
    prompt2 = textwrap.dedent(prompt2).strip()
    
    messages = add_message(prompt1, "user", [])
    prev_content = send_message("gpt-4o", messages).choices[0].message.content
    messages = add_message(prev_content, "user", messages)
    
    #need to chain previous result
    
    #full_prompt = f"{prompt2}\n\nPrevious Output: {prev_content}"
    #messages = add_message(full_prompt, "user", [])
    messages = add_message(prompt2, "user", messages)
    prev_content = send_message("gpt-4o", messages).choices[0].message.content
    messages = add_message(prev_content, "user", messages)
    
    
    # full_prompt = f"{prompt3}\n\nPrevious Output: {prev_content}"
    # messages = add_message(prompt3, "user", messages)
    messages = add_message("This is the given relation set: " + Relation_Set, "system", General_Msg)
    messages = add_message(prompt3, "user", messages)
    result = parse_message("gpt-4o", messages, KGFormat)
    
    return result.choices[0].message.parsed

def generate_kg_n_times(prompt, n):
    knowledge_graphs = []
    for i in range(n):
        result = generate_kg(prompt)
        knowledge_graphs.append(result.knowledge_graph)
    combined_kg = cluster.construct_best_knowledge(knowledge_graphs)
    return combined_kg
   
def generate_analogy_separate(bg):
    prompt1 = f"""
    Take this step-by-step recipe for analogy generation:
    
    1. With the given concept and summary, generate ten analogies based on your understanding, from different perspectives, which can be related to the background information {bg}. Put them in the "Analogies" field.
    2. For each analogy, combined with the generated Concept Knowledge Graph to coin a knowledge graph. The generation should adhere to the structure of the Concept Knowledge Graph, while maintaining its own terminology and concepts. Each Knowledge graph should be comprehensive, self-contained, and concise, formatted as triplets `entity, relation, entity`, and separated by a new line. Put the triplets in the "Analogies_KnowledgeGraphs" field. Make sure to include any prior knowledge that is necessary to understand the analogy but not part of the original summary; include the connectivity of the resulting knowledge graph by inserting bridging concepts and relations to connect as many nodes as possible.
    """
    
    prompt2 = """
    Take this step-by-step recipe for analogy filtering:
    
    1. Based on the given analogies, filter, rank, and find the top three analogies that has the most similar structure as the given original concept and semantically different from each other. Put their concepts in the "concept" field and their detailed summaries in the "summary" field.
    2. For each analogy, extract the words that resemble the analogy(why are they analogous) and put them in the "terminology" field.
    """
    
    messages = add_message(prompts.SYSTEM_INSTRUCTION_ANALOGY, "system", General_Msg)
    messages = add_message(prompt1, "user", messages)
    prev_content = parse_message("gpt-4o", messages, AnalogyFormat).choices[0].message.content
    
    #chain previous result
    #full_prompt = f"{prompt2}\n\nPrevious Output: {prev_content}"
    messages = add_message("This is the given relation set: " + Relation_Set, "system", General_Msg)
    messages = add_message(prompt2, "user", messages)
    result = parse_message("gpt-4o", General_Msg, FilteredAnalogy)
    return result.choices[0].message.parsed 

def draw_kg(kg, ax=None):
    G = nx.DiGraph()
    for triplet in kg.split('\n'):
        try:
            entity1, relation, entity2 = triplet.strip().split(',')
            G.add_edge(entity1.strip(), entity2.strip(), label=relation.strip())
        except ValueError as e:
            print(f"Skipping invalid triplet: {triplet}, error: {e}")

    #pos = nx.spring_layout(G, seed=1, iterations=1_000)
    pos = nx.forceatlas2_layout(G, max_iter=1_000)
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
    
def set_up():
    add_message(prompts.SYSTEM_INSTRUCTION, "system", General_Msg)
    add_message("You have read Gentner's Structure Mapping theory and Hofstadter's Analogy theory very well and is a master in this field.", "user", General_Msg)
    
    #some image few-shot
    add_image(encode_image("fig1.png"), "user", General_Msg, "Example of Structure Mapping")
    add_image(encode_image("fig2.png"), "user", General_Msg, "Example of Analogy")
    
    #some verbal few-shot
    add_message(prompts.FEW_SHOT_PROMPT, "system", General_Msg)
    
    #some csv few-shot
    with open("analogy_mappings_final.csv", "r") as f:
        analogies = f.read()
    add_message(analogies, "user", f"""{prompts.PROMPT_FOR_GOOD_ANALOGIES} {analogies}""")
    
def concept_gen(concept):
    global Relation_Set
    global Analogy_KG
    set_up()
    generate_summary(concept)
    event = generate_kg(concept)
    #graph = generate_kg_n_times(concept, 2)
    #event.knowledge_graph = graph
    Relation_Set += event.relation_set
    Analogy_KG = event.knowledge_graph
    print(event)
    return event.concept, event.summary, event.knowledge_graph

def analogy_gen(bg):
    # analogies_kg = generate_analogy()
    # clean_up()
    # return analogies_kg.Filtered_Analogies, analogies_kg.Filtered_Analogies_Explanation, analogies_kg.Filtered_Analogies_KnowledgeGraphs
    global Analogy_KG
    analogies = generate_analogy_separate(bg)
    for i in range(0, len(analogies.concept)):
        event = generate_analogy_kg(analogies.concept[i])
        Analogy_KGs.append(event.knowledge_graph)
    
        #eval_scores.append(calculate_graph_edit_distance(Analogy_KG, event.knowledge_graph))
        #add evaluation to the knowledge graph
        
    return analogies.concept, analogies.summary, Analogy_KGs, analogies.terminology

def calculate_graph_edit_distance_by_index(analogy_index):
    global Analogy_KG
    dis = calculate_graph_edit_distance_optimized(Analogy_KG, Analogy_KGs[int(analogy_index)])
    print(dis)
    return dis

def calculate_graph_edit_distance_optimized(triplets1, triplets2):
    nxg1 = draw_kg(triplets1)
    nxg2 = draw_kg(triplets2)
    for v in similarity.optimize_graph_edit_distance(nxg1, nxg2):
        print("loop" + str(v))
        minv = v
    return minv

def calculate_graph_edit_distance(triplets1, triplets2):
    G1 = nx.DiGraph()
    for triplet in triplets1.split('\n'):
        try:
            entity1, relation, entity2 = triplet.strip().split(',')
            G1.add_edge(entity1.strip(), entity2.strip(), label=relation.strip())
        except ValueError as e:
            print(f"Skipping invalid triplet: {triplet}, error: {e}")
            
    G2 = nx.DiGraph()
    for triplet in triplets2.split('\n'):
        try:
            entity1, relation, entity2 = triplet.strip().split(',')
            G2.add_edge(entity1.strip(), entity2.strip(), label=relation.strip())
        except ValueError as e:
            print(f"Skipping invalid triplet: {triplet}, error: {e}")
    
    return nx.graph_edit_distance(G1, G2)
   # return similarity.optimize_graph_edit_distance(G1, G2)
    



def clean_up():
    global General_Msg
    global Relation_Set
    General_Msg.clear()
    Relation_Set = ""
    
if __name__ == "__main__":
    concept = "Matrix Factorization"
    # concept_gen(concept)
    # result = analogy_gen()
    # print(result)
    
    #generation for KG
    #event = generate_kg(concept)
    #print(event)
    # nxg = draw_kg(event.knowledge_graph)
    # plt.tight_layout()
    # plt.show()
    
    
    #generation for Analogies
    # analogies_kg = generate_analogy()
    # print(analogies_kg)
    
    
    # draw_kg_list([analogies_kg.Filtered_Analogies_KnowledgeGraphs[0], analogies_kg.Filtered_Analogies_KnowledgeGraphs[1], analogies_kg.Filtered_Analogies_KnowledgeGraphs[2]])
    # print(General_Msg)
    # nxg1 = draw_kg(analogies_kg.KnowledgeGraph1)
    # nxg2 = draw_kg(analogies_kg.KnowledgeGraph2)
    # nxg3 = draw_kg(analogies_kg.KnowledgeGraph3)
    
    # for v in similarity.optimize_graph_edit_distance(nxg, nxg1):
    #     minv = v
    # print(minv)
    
    
    #print(analogies_kg)
    # kernel = gk.graph_from_networkx(nxg)
    # gk.GraphKernel("random_walk", with_labels=True).fit_transform([kernel])

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

# def get_response(prompt):
#     try:
#         response = client.chat.completions.create(
#             model= "gpt-4o",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0,
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return None

#def prompt_chain(initial_prompt, prompts):
#     messages = add_message(prompts.SYSTEM_INSTRUCTION, "system", [])
#     messages = add_message(initial_prompt, "user", messages)
#     result = send_message("gpt-4o", messages).choices[0].message.content
    
#     for i, prompt in enumerate(prompts, 1):
#         full_prompt = f"{prompt}\n\nPrevious Output: {result}"
#         messages = add_message(full_prompt, "user", [])
#         result = send_message("gpt-4o", messages).choices[0].message.content
#         if result is None:
#             return f"Prompt {i} failed to generate a response."
#     return result


# def generate_analogy(background_info=""):
#     prompt1 = f"""
#     Take this step-by-step recipe for analogy generation:
    
#     1. With the given concept and summary, generate ten analogies based on your understanding. The analogy should be tied to user's background information: {background_info}. Put them in the "Analogies" field.
#     2. For each analogy, combined with the generated Concept Knowledge Graph to coin a knowledge graph. The generation should adhere to the structure of the Concept Knowledge Graph, while maintaining its own terminology and concepts. Each Knowledge graph should be comprehensive, self-contained, and concise, formatted as triplets `entity, relation, entity`, and separated by a new line. Put the triplets in the "Analogies_KnowledgeGraphs" field. Make sure to include any prior knowledge that is necessary to understand the analogy but not part of the original summary; include the connectivity of the resulting knowledge graph by inserting bridging concepts and relations to connect as many nodes as possible. Do not include the original concept in the graph.
#     """
    
#     prompt2 = """
#     Take this step-by-step recipe for analogy filtering:
    
#     1. Based on the given analogies, rate how helpful they are in helping the users understand the original concept, from 0 to 10.
#     2. Based on the ratings, rank and find the top three analogies that has the most similar structure as the given original concept and semantically different from each other. Put their concepts in the "Filtered_Analogies" field.
#     3. For each analogy, turn it into a knowledge graph. Starting only from a summary of the concept, Each Knowledge graph should be comprehensive, self-contained, and concise, formatted as triplets `entity, relation, entity`, and separated by a new line. Put the triplets in the "Filtered_Analogies_KnowledgeGraphs" field. Make sure to include any prior knowledge that is necessary to understand the analogy but not part of the original summary; include the connectivity of the resulting knowledge graph by inserting bridging concepts and relations to connect as many nodes as possible. Follow the Given Relation Set to prune the trivial entities and relations and keep a more deep relationship graph.
#     """
    
#     messages = add_message(prompts.SYSTEM_INSTRUCTION_ANALOGY, "system", General_Msg)
#     messages = add_message(prompt1, "user", messages)
#     prev_content = parse_message("gpt-4o", messages, AnalogyFormat).choices[0].message.content
    
#     #chain previous result
#     #full_prompt = f"{prompt2}\n\nPrevious Output: {prev_content}"
#     messages = add_message("This is the given relation set: " + Relation_Set, "system", General_Msg)
#     messages = add_message(prompt2, "user", messages)
#     result = parse_message("gpt-4o", General_Msg, FilteredAnalogyFormat)
#     return result.choices[0].message.parsed