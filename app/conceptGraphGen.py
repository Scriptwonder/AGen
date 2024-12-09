import os
import textwrap
import openai as OpenAI
import utils    
from pydantic import BaseModel
from typing import Literal
import prompts
import json
import networkx as nx
from pyvis.network import Network

SUBJECTS = "Quantum Superposition"
AUDIENCE = "College Students"
N=5

PK = None
TX = None
PG = None

class Analogy(BaseModel):
    analogy_concept: list[str]
    analogy_explanation: list[str]
    analogy_content: list[str]

class Taxonomy(BaseModel):
    class Relation(BaseModel):
        relation: str
        direction: Literal["directed", "undirected"]
        
    concepts: list[str]
    relations: list[Relation]

class KnowledgeGraph(BaseModel):
    class Knowledge(BaseModel):
        head: str
        relation: str
        tail: str

    knowledge: list[Knowledge]

def sample_background(subject, audience):
    response = utils.send_message(messages=[
            {"role": "user", "content": prompts.SAMPLE_BG_PROMPT.format(subject=subject, audience=audience)}
    ], n=N)
    articles = [f"<article {idx}>\n{article.strip()}\n<article {idx}>" for idx, article in enumerate((i.message.content for i in response.choices), start=1)]
    return articles

def combine_knowledge(subject, articles):
    response = utils.send_message(messages=[
        {"role": "user", "content": prompts.COMBINE_PROMPT.format(subject=subject, articles="\n\n".join(articles))}
    ])
    return response.choices[0].message.content
    
def Chain_of_Note_Analysis(background_knowledge):
    response = utils.send_message(messages=[
        {"role": "user", "content": prompts.CoN_BG_PROMPT.format(subject=SUBJECTS, article=background_knowledge)}
    ])
    return response.choices[0].message.content

def Taxonomy_Creation(parsed_knowledge):
    response = utils.parse_message(format=Taxonomy, messages=[
        {"role": "user", "content": prompts.TAXONOMY_PROMPT.format(subject=SUBJECTS, knowledge=parsed_knowledge)}
    ])
    return response.choices[0].message.parsed

def graph_creation(parsed_taxonomy, parsed_knowledge):
    concepts = "\n".join(f"- {concept}" for concept in parsed_taxonomy.concepts)
    relations = "\n".join(f"- {relation.relation} ({relation.direction})" for relation in parsed_taxonomy.relations)
    response = utils.parse_message(format=KnowledgeGraph, messages=[
        {"role": "user", "content": prompts.GRAPH_CREATION_PROMPT.format(subject=SUBJECTS, concepts=concepts, relations=relations, knowledge=parsed_knowledge)}
    ])
    return response.choices[0].message.parsed

# def visualization(parsed_taxonomy, knowledge_graph):
#     kg = nx.DiGraph()

#     relation_lookup = {relation.relation: relation.direction for relation in parsed_taxonomy.relations}

#     for knowledge in knowledge_graph.knowledge:
#         direction = relation_lookup.get(knowledge.relation, "directed")

#         kg.add_edge(knowledge.head, knowledge.tail, label=knowledge.relation)
#         if direction == "undirected":
#             kg.add_edge(knowledge.tail, knowledge.head, label=knowledge.relation)
            
#     g = Network(height=1200, width=1200, directed=True)

#     g.from_nx(kg)

def export_graph_to_json(parsed_taxonomy, knowledge_graph, parsed_knowledge):
    kg = nx.DiGraph()

    relation_lookup = {relation.relation: relation.direction for relation in parsed_taxonomy.relations}

    for knowledge in knowledge_graph.knowledge:
        direction = relation_lookup.get(knowledge.relation, "directed")
        kg.add_edge(knowledge.head, knowledge.tail, label=knowledge.relation)
        if direction == "undirected":
            kg.add_edge(knowledge.tail, knowledge.head, label=knowledge.relation)

    # Convert the graph to a JSON-serializable format
    graph_data = {
        "nodes": [{"id": node} for node in kg.nodes],
        "links": [{"source": edge[0], "target": edge[1], "label": kg.edges[edge]["label"]} for edge in kg.edges],
        "Graph_Knowledge": parsed_knowledge
    }
    return graph_data

def export_graph_to_json_new(knowledge_graph, analogy_concept, analogy_content):
    kg = nx.DiGraph()

    for knowledge in knowledge_graph.knowledge:
        kg.add_edge(knowledge.head, knowledge.tail, label=knowledge.relation)

    # Convert the graph to a JSON-serializable format
    graph_data = {
        "nodes": [{"id": node} for node in kg.nodes],
        "links": [{"source": edge[0], "target": edge[1], "label": kg.edges[edge]["label"]} for edge in kg.edges],
        "Analogy_Concept": analogy_concept,
        "Analogy_Content": analogy_content
    }
    return graph_data
    

def generate_analogy(parsed_knowledge, audience, taxonomy):
    # response = utils.parse_message(format=Analogy, messages=[
    #     {"role": "user", "content": prompts.ANALOGY_GENERATION_PROMPT.format(knowledge=parsed_knowledge, audience=audience)}
    # ])
    response = utils.parse_message(format=Analogy, messages=[
        {"role": "user", "content": prompts.ANALOGY_GENERATION_PROMPT_2.format(concept=SUBJECTS, knowledge=parsed_knowledge, audience=audience, taxonomy = taxonomy, number = N)}
    ])
    return response.choices[0].message.content

def generate_analogy_graph(analogy):
    
    background_knowledge = sample_background(analogy, AUDIENCE)
    
    # Combine the background knowledge
    combined_knowledge = combine_knowledge(analogy, background_knowledge)
    
    parsed_knowledge = Chain_of_Note_Analysis(combined_knowledge)
    
    #print(parsed_knowledge)
    
    parsed_taxonomy = Taxonomy_Creation(parsed_knowledge)
    
    parsed_graph = graph_creation(parsed_taxonomy, parsed_knowledge)
    
    return export_graph_to_json(parsed_taxonomy, parsed_graph, parsed_knowledge)

def generate_analogy_graphs( audience = AUDIENCE, parsed_knowledge = PK, taxonomy = TX):
    global PK
    if parsed_knowledge is None:
        parsed_knowledge = PK
    global TX
    if taxonomy is None:
        taxonomy = TX
    analogy = generate_analogy(parsed_knowledge, audience, taxonomy)
    graph_summary = []
    
    data = json.loads(analogy)
    concepts = data.get("concept", [])
    analogies = data.get("analogy", [])
    result = []
    for i, analogy in enumerate(analogies):
        concept = concepts[i % len(concepts)] if concepts else "Unknown Concept"
        result.append({"concept": concept, "analogy": analogy})
    
    for i in range(3):
        graph_summary.append(generate_analogy_graph(result[i]))
    
    return graph_summary

def generate_analogy_graphs_new(combined_knowledge=PK, parsed_graph=PG):
    global PK
    if combined_knowledge is None:
        combined_knowledge = PK
    global PG
    if parsed_graph is None:
        parsed_graph = PG
    
    response = utils.parse_message(format=Analogy, messages=[
        {"role": "user", "content": prompts.ANALOGY_GENERATION_PROMPT_3.format(concept=SUBJECTS, knowledge=combined_knowledge, audience=AUDIENCE, number = N)}
    ])
    analogies = json.loads(response.choices[0].message.content)
    response = utils.parse_message(format=Analogy, messages=[
        {"role": "user", "content": prompts.ANALOGY_GENERATION_PROMPT_4.format(concept=SUBJECTS, analogies = analogies, audience=AUDIENCE)}
    ])
    filtered_analogies = json.loads(response.choices[0].message.content)
    #print(filtered_analogies)
    
    analogy_concept = filtered_analogies.get("analogy_concept", [])
    analogy_content = filtered_analogies.get("analogy_content", [])
    
    result = []
    for i, concept in enumerate(analogy_concept):
        # concept = analogy_concept[i % len(analogy_concept)]
        # analogy = analogy_content[i % len(analogy_content)]
        response = utils.parse_message(format=KnowledgeGraph, messages=[
        {"role": "user", "content": prompts.ANALOGY_GRAPH_PROMPT.format(concept=SUBJECTS, graph = parsed_graph, analogy_concept = concept, analogy_content = analogy_content[i])}
        ])
        result.append(export_graph_to_json_new(response.choices[0].message.parsed, analogy_content[i], concept))
    return result

def main(subjects=SUBJECTS, audience=AUDIENCE):
    # Sample background knowledge
    background_knowledge = sample_background(subjects, audience)
    
    # Combine the background knowledge
    combined_knowledge = combine_knowledge(subjects, background_knowledge)
    
    # Chain of Note Analysis
    parsed_knowledge = Chain_of_Note_Analysis(combined_knowledge)
    
    global PK
    PK = combined_knowledge
    
    # Taxonomy Creation
    parsed_taxonomy = Taxonomy_Creation(parsed_knowledge)
    global TX
    TX = parsed_taxonomy
    
    # Graph Creation
    parsed_graph = graph_creation(parsed_taxonomy, parsed_knowledge)
    global PG
    PG = parsed_graph
    
    return export_graph_to_json(parsed_taxonomy, parsed_graph, parsed_knowledge)
    
    #visualization
    #visualization(parsed_taxonomy, parsed_graph)
    
if __name__ == "__main__":
    main()
    generate_analogy_graphs_new(PK, PG)
    #generate_analogy_graphs()
    # background_knowledge = sample_background(SUBJECTS, AUDIENCE)
    
    # # Combine the background knowledge
    # combined_knowledge = combine_knowledge(SUBJECTS, background_knowledge)
    
    # response = utils.parse_message(format=Analogy, messages=[
    #     {"role": "user", "content": prompts.ANALOGY_GENERATION_PROMPT_3.format(concept=SUBJECTS, knowledge=combined_knowledge, audience=AUDIENCE, number = N)}
    # ])
    # analogies = json.loads(response.choices[0].message.content)
    # response = utils.parse_message(format=Analogy, messages=[
    #     {"role": "user", "content": prompts.ANALOGY_GENERATION_PROMPT_4.format(concept=SUBJECTS, analogies = analogies, audience=AUDIENCE)}
    # ])
    # filtered_analogies = json.loads(response.choices[0].message.content)
    # print(filtered_analogies)
    
    # analogy_concept = filtered_analogies.get("analogy_concept", [])
    # analogy_content = filtered_analogies.get("analogy_content", [])
    
    
    #  # Chain of Note Analysis
    # parsed_knowledge = Chain_of_Note_Analysis(combined_knowledge)
    # PK = combined_knowledge
    
    # # Taxonomy Creation
    # parsed_taxonomy = Taxonomy_Creation(parsed_knowledge)
    # TX = parsed_taxonomy
    
    # # Graph Creation
    # parsed_graph = graph_creation(parsed_taxonomy, parsed_knowledge)
    
    # #print(parsed_graph)
    
    # response = utils.parse_message(format=KnowledgeGraph, messages=[
    #     {"role": "user", "content": prompts.ANALOGY_GRAPH_PROMPT.format(concept=SUBJECTS, graph = parsed_graph, analogy_concept = analogy_concept[0], analogy_content = analogy_content[0])}
    # ])
    
    #print(response.choices[0].message.parsed)



