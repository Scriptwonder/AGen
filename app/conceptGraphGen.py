import os
import textwrap
import openai as OpenAI
import utils    
from pydantic import BaseModel, Field, ValidationError
from typing import Literal
import prompts
import json
import networkx as nx
from pyvis.network import Network

SUBJECTS = "Filter Bubble"
AUDIENCE = "Undergraduate Students"
N=5
Analogy_Sampling_Number = 10
Analogy_Filtered_Number = 5

PK = None
TX = None
PG = None

class EvaluationDimension(BaseModel):
    score: int = Field(..., description="Score from 1 to 5")
    comment: str = Field(..., description="Comment on the evaluation")
    
class Dimensions(BaseModel):
    """
    Contains all six dimensions of Gentner-based analogy evaluation.
    """
    StructuralAlignment: EvaluationDimension
    ProgressiveAlignmentPotential: EvaluationDimension
    CommonalitiesAndDifferences: EvaluationDimension
    AbstractionLevelAndLearnerReadiness: EvaluationDimension
    ClarityAndEngagement: EvaluationDimension
    FacilitationOfTransfer: EvaluationDimension
    
class AnalogyEvaluation(BaseModel):
    analogy_concept: str
    analogy_content: str
    dimensions: Dimensions
    overallScore: int = Field(..., description="Overall score from 1 to 60")
    overallAssessment: str
    suggestions: str
    
class AnalogyGen(BaseModel):
    Analogy: str
    Explanation: str
    Causal_Relationship: str
    Image_Generation_Prompt: str
    
class AnalogyCluster(BaseModel):
    Scratch_Pad: str | None
    Analogy: list[str]
    Explanation: list[str]
    Causal_Relationship: list[str]
    Image_Generation_Prompt: list[str]
    
def compressAnalogyEvaluation(analogy):
    #Compress one AnalogyEvaluation object into a string
    dimensions = analogy.get("dimensions", "")
    return f"""
    Structural Alignment: {dimensions.get("StructuralAlignment", "").get("score", "")}  
    {dimensions.get("StructuralAlignment", "").get("comment", "")}
    
    Progressive Alignment Potential: {dimensions.get("ProgressiveAlignmentPotential", "").get("score", "")} 
    {dimensions.get("ProgressiveAlignmentPotential", "").get("comment", "")}
    
    Commonalities and Differences: {dimensions.get("CommonalitiesAndDifferences", "").get("score", "")} 
    {dimensions.get("CommonalitiesAndDifferences", "").get("comment", "")}
    
    Abstraction Level and Learner Readiness: {dimensions.get("AbstractionLevelAndLearnerReadiness", "").get("score", "")} 
    {dimensions.get("AbstractionLevelAndLearnerReadiness", "").get("comment", "")}
    
    Clarity and Engagement: {dimensions.get("ClarityAndEngagement", "").get("score", "")} 
    {dimensions.get("ClarityAndEngagement", "").get("comment", "")}
    
    Facilitation of Transfer: {dimensions.get("FacilitationOfTransfer", "").get("score", "")} 
    {dimensions.get("FacilitationOfTransfer", "").get("comment", "")}
    
    Overall Score: {analogy.get("overallScore", "")} 
    
    Overall Assessment: {analogy.get("overallAssessment", "")} 
    
    Suggestions: {analogy.get("suggestions", "")}
    
    """

class AnalogyEvaluationGroup(BaseModel):
    analogies: list[AnalogyEvaluation]

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

def combine_knowledge(subject, audience, articles):
    response = utils.send_message(messages=[
        {"role": "user", "content": prompts.COMBINE_PROMPT.format(subject=subject, audience=audience, articles="\n\n".join(articles))}
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

def export_graph_to_json_new(knowledge_graph, analogy_concept, analogy_content, evaluation_result):
    kg = nx.DiGraph()

    for knowledge in knowledge_graph.knowledge:
        kg.add_edge(knowledge.head, knowledge.tail, label=knowledge.relation)

    # Convert the graph to a JSON-serializable format
    graph_data = {
        "nodes": [{"id": node} for node in kg.nodes],
        "links": [{"source": edge[0], "target": edge[1], "label": kg.edges[edge]["label"]} for edge in kg.edges],
        "Analogy_Concept": analogy_concept,
        "Analogy_Content": analogy_content,
        "Evaluation_Result": evaluation_result
        
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
    combined_knowledge = combine_knowledge(analogy, AUDIENCE, background_knowledge)
    
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
    
    response = utils.send_message(messages= [
            {"role": "user", "content": prompts.ANALOGY_WARNING_PROMPT.format(audience=AUDIENCE)}
    ])
    proposed_metric = prompts.ANALOGY_WARNING_PROMPT + response.choices[0].message.content
    response = utils.parse_message(format=Analogy, messages=[
        {"role": "user", "content": proposed_metric+prompts.ANALOGY_GENERATION_PROMPT_3.format(concept=SUBJECTS, knowledge=combined_knowledge, audience=AUDIENCE, number = Analogy_Sampling_Number)}
    ])
    analogies = json.loads(response.choices[0].message.content)
    
    analogies_evaluated_and_filtered = json.loads(evaluate_analogy(analogies)).get("analogies", [])
    
    
    
    # response = utils.parse_message(format=Analogy, messages=[
    #     {"role": "user", "content": prompts.ANALOGY_GENERATION_PROMPT_4.format(concept=SUBJECTS, analogies = analogies, audience=AUDIENCE)}
    # ])
    # filtered_analogies = json.loads(response.choices[0].message.content)
    #print(filtered_analogies)
    # analogy_concept = filtered_analogies.get("analogy_concept", [])
    # analogy_content = filtered_analogies.get("analogy_content", [])
    
    result = []
    for i, _ in enumerate(analogies_evaluated_and_filtered):
        concept = analogies_evaluated_and_filtered[i].get("analogy_concept")
        content = analogies_evaluated_and_filtered[i].get("analogy_content")
        response = utils.parse_message(format=KnowledgeGraph, messages=[
        {"role": "user", "content": prompts.ANALOGY_GRAPH_PROMPT.format(concept=SUBJECTS, graph = parsed_graph, analogy_concept = concept, analogy_content = content)}
        ])
        evaluation_result = compressAnalogyEvaluation(analogies_evaluated_and_filtered[i])
        result.append(export_graph_to_json_new(response.choices[0].message.parsed, content, concept, evaluation_result))
    return result

def evaluate_single_analogy(analogy_concept, analogy_content, original_concept=SUBJECTS, audience = AUDIENCE):
    response = utils.parse_message(format=AnalogyEvaluation, messages=[
        {"role": "user", "content": prompts.ANALOGY_EVALUATION_PROMPT.format(analogy_concept = analogy_concept, analogy_content = analogy_content, origin = original_concept, audience = audience)}
    ])
    return response.choices[0].message.content

def evaluate_analogy(analogy, original_concept=SUBJECTS, audience = AUDIENCE):
    evaluation_result = []
    analogy_concept = analogy.get("analogy_concept", "")
    analogy_content = analogy.get("analogy_content", "")
    #we first evaluate the analogy one by one
    for i, _ in enumerate(analogy_concept):
        single_concept = analogy_concept[i]
        single_content = analogy_content[i]
        evaluation_result.append(evaluate_single_analogy(single_concept, single_content, original_concept, audience))
    
    print(evaluation_result)
    
    #now we get the n evaluated analogies, filter them and return
    response = utils.parse_message(format=AnalogyEvaluationGroup, messages=[
        {"role": "user", "content": prompts.ANALOGY_FILTER_PROMPT.format(n = Analogy_Sampling_Number, filtered_n = Analogy_Filtered_Number)}
    ])
    evaluation_result = response.choices[0].message.content
    
    print(evaluation_result)

    return evaluation_result    


def generate_analogy_new(audience, concept, combined_knowledge):
    response = utils.parse_message(format=AnalogyCluster, messages=[
        {"role": "user", "content": prompts.ANALOGY_PRINCIPLE_PROMPT.format(audience=audience, concept=concept, combined_knowledge=combined_knowledge, n=Analogy_Sampling_Number)}
    ])
    return response.choices[0].message.content

def filter_analogy_new(audience, analogies, taxonomy):
    response = utils.parse_message(format=AnalogyCluster, messages=[
        {"role": "user", "content": prompts.ANALOGY_FILTER_PROMPT_NEW.format(audience=audience, taxonomy=taxonomy, analogies=analogies, n=Analogy_Filtered_Number)}
    ])
    return response.choices[0].message.content
    

def evaluate_analogy_new(analogy, subject):
    res = ""
    response = utils.send_message(messages=[
        {"role": "user", "content": prompts.EVALUATION_BENCHMARK_OAMN + "\n" + analogy}
    ])
    res += "\n" + response.choices[0].message.content
    response = utils.send_message(messages=[
        {"role": "user", "content": prompts.EVALUATION_BENCHMARK_MANAED + "\n" + analogy}
    ])
    res += "\n" + response.choices[0].message.content
    response = utils.send_message(messages=[
        {"role": "user", "content": prompts.EVALUATION_BENCHMARK_USEFULNESS + "\n" + analogy}
    ])
    res += "\n" + response.choices[0].message.content
    response = utils.send_message(messages=[
        {"role": "user", "content": prompts.EVALUATION_BENCHMARK_ACCURACY.format(concept=subject) + "\n" + analogy}
    ])
    res += "\n" + response.choices[0].message.content
    
    combined_res = utils.send_message(messages=[
        {"role": "user", "content": prompts.EVALUATION_COMBINATION_PROMPT.format(evaluation = res)}
    ])
    return combined_res.choices[0].message.content


def main(subjects=SUBJECTS, audience=AUDIENCE):
    # Sample background knowledge
    background_knowledge = sample_background(subjects, audience)
    
    # Combine the background knowledge
    combined_knowledge = combine_knowledge(subjects, audience, background_knowledge)
    
    # Chain of Note Analysis
    parsed_knowledge = Chain_of_Note_Analysis(combined_knowledge)
    
    global PK
    PK = combined_knowledge
    
    # Taxonomy Creation
    parsed_taxonomy = Taxonomy_Creation(parsed_knowledge)
    global TX
    TX = parsed_taxonomy
    
    #new way
    new_analogy = generate_analogy_new(audience, subjects, combined_knowledge)
    #print(new_analogy)
    filtered_analogies = filter_analogy_new(audience, new_analogy, parsed_taxonomy)
    print(filtered_analogies)
    
    analogies = json.loads(filtered_analogies).get("Analogy", "")
    explanations = json.loads(filtered_analogies).get("Explanation", "")
    
    analogy_prompt = json.loads(filtered_analogies).get("Analogy", "")
    eval_res = []
    for analogy, explanation in zip(analogies, explanations):
        item = f"{analogy}\n{explanation}"
        eval_res.append(evaluate_analogy_new(item, subjects))
    print(eval_res)
    
    image_prompt = json.loads(filtered_analogies).get("Image_Generation_Prompt", "")
    image_res = []
    for item in image_prompt:
        image_res.append(utils.generate_image(item))
    print(image_res)
    
    
    return (analogies, explanations, eval_res, image_res)
    
    
    
    
    # # Graph Creation
    # parsed_graph = graph_creation(parsed_taxonomy, parsed_knowledge)
    # global PG
    # PG = parsed_graph
    
    # return export_graph_to_json(parsed_taxonomy, parsed_graph, parsed_knowledge)
    
    #visualization
    #visualization(parsed_taxonomy, parsed_graph)
    
if __name__ == "__main__":
    main()
    #generate_analogy_graphs_new(PK, PG)
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



