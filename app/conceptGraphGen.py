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
import pandas as pd
from scipy.stats import wilcoxon

SUBJECTS = "Dataflow in Computer Networks"
AUDIENCE = "Graduate STEM Student"
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
    #print(background_knowledge)
    
    # Combine the background knowledge
    combined_knowledge = combine_knowledge(subjects, audience, background_knowledge)
    #print(combined_knowledge)
    
    # Chain of Note Analysis
    parsed_knowledge = Chain_of_Note_Analysis(combined_knowledge)
    #print(parsed_knowledge)
    
    global PK
    PK = combined_knowledge
    
    # Taxonomy Creation
    parsed_taxonomy = Taxonomy_Creation(parsed_knowledge)
    global TX
    TX = parsed_taxonomy
    #print(parsed_taxonomy)
    
    #new way
    new_analogy = generate_analogy_new(audience, subjects, combined_knowledge)
    #print(new_analogy)
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
        #print(eval_res)
        #return (analogy+explanation, eval_res)
    #print(eval_res)
    
    image_prompt = json.loads(filtered_analogies).get("Image_Generation_Prompt", "")
    image_res = []
    for item in image_prompt:
        print(item)
        image_res.append(utils.generate_image(item))
    print(image_res)
    return (analogies, explanations, eval_res, image_res)
    #return (analogies, explanations)
    
    # # Graph Creation
    # parsed_graph = graph_creation(parsed_taxonomy, parsed_knowledge)
    # global PG
    # PG = parsed_graph
    # return export_graph_to_json(parsed_taxonomy, parsed_graph, parsed_knowledge)
    
    #visualization
    #visualization(parsed_taxonomy, parsed_graph)
    
def create_table(data):
    df = pd.DataFrame(data)
    df.to_csv("analogy_data.csv", index=False)
    return df
    
if __name__ == "__main__":
    main(subjects=SUBJECTS, audience=AUDIENCE)
    
    # import itertools
    # concept = ["Earth’s Layers",
    #     "Photosynthesis", "Periodic Table Trends"
    # ]
    # concept1 = concept[::-1]
    # audience_descriptions = [f"{group} who is interested in {habit}" for group, habit in itertools.product(utils.groups, utils.habits)]
    # import csv
    # csv_file_path = "analogy_data.csv"
    # i=0
    # with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(["Concept", "Audience", "Analogy", "Explanation"])
    #     for subject in concept1:
    #         for audience in audience_descriptions:
    #             analogies, explanations = main(subject, audience)
    #             writer.writerow([subject, audience, analogies, explanations])
    #             i+=1
    #             print(i)
    
    # Original data from the table
    # group1_scores = [
    #     [2, 3, 3, 4, 3, 2],  # Tug of War vs Magnetic Attraction
    #     [4, 2, 4, 4, 4, 4],  # Solar System as Clockwork
    #     [2, 3, 3, 4, 3, 2],  # Solid as a Symphony Orchestra
    #     [4, 3, 4, 4, 4, 3],  # SDLC as Plant Life Cycle
    #     [3, 2, 4, 4, 4, 4],  # Energy Flow as Water Pipes
    #     [4, 3, 4, 4, 4, 4],  # Ecosystem as Computer Network
    #     [3, 2, 4, 4, 4, 4],  # Cell as Biological Factory
    #     [3, 3, 4, 4, 4, 3],  # Forces & Motion as Symphony Orchestra
    #     [4, 3, 4, 4, 4, 3],  # Earth as High-Tech Computer
    #     [4, 2, 4, 4, 4, 4],  # Photosynthesis as Solar-Powered Factory
    #     [4, 2, 4, 4, 4, 4],  # Periodic Table as City Map
    #     [4, 2, 4, 4, 4, 4],  # DNA as Computer Code
    #     [3, 2, 4, 4, 4, 3],  # Climate as Complex Computer System
    #     [3, 3, 4, 4, 4, 3.5], # Limits as Camera Zoom
    #     [3, 3, 4, 4, 4, 3.5], # Uncertainty Principle as Blurry Photo
    #     [4, 3, 4, 4, 4, 4],  # Thermodynamics as Budget
    #     [3, 2, 4, 4, 4, 3],  # Deep Learning as Neural Network
    # ]

    # group2_scores = [
    #     [2, 3, 3, 4, -1, 4], # Toy Car on Ramp (Force & Motion)
    #     [3, 3, 4, 4, 4, 3],  # Sky as Clock (Celestial Movements)
    #     [3, 2, 4, 4, 4, 4],  # Ice Melting as Popsicle Melting
    #     [3, 2, 4, 4, 4, 4],  # Butterfly Life Cycle as Story
    #     [2, 3, 4, 4, 4, 3.5],# Heating Pan as Passing Torch
    #     [4, 2, 4, 4, 4, 4],  # Ecosystem as Web
    #     [3, 2, 4, 4, 4, 4],  # Cell as Factory
    #     [1, 1, 4, 4, 3, 3],  # Path of Soccer Ball
    #     [4, 2, 4, 4, 4, 4],  # Earth Layers as Hard-Boiled Egg
    #     [3, 2, 4, 4, 4, 4],  # Plant as Solar Panel
    #     [3, 3, 4, 4, 4, 4],  # Periodic Table as Family Reunion
    #     [3, 2, 4, 4, 4, 4],  # DNA as Recipe Book
    #     [4, 2, 4, 4, 4, 4],  # Greenhouse Gases as Blanket
    #     [3, 2, 4, 4, 4, 4],  # Limits as Zooming on Curve
    #     [3, 3, 4, 4, 4, 3],  # Electrons as Student Decisions
    #     [3, 3, 3.5, 4, 4, 4],# Engine as Chef
    #     [3, 2, 4, 4, 4, 4],  # Training AI as Teaching Child
    # ]

    # # Perform Wilcoxon test for each pair and store the results
    # wilcoxon_results_adjusted = []
    # for g1, g2 in zip(group1_scores, group2_scores):
    #     try:
    #         stat, p_value = wilcoxon(g1, g2, zero_method='zsplit')  # Adjusted zero_method
    #         wilcoxon_results_adjusted.append({"Wilcoxon Statistic": stat, "p-value": p_value})
    #     except ValueError as e:
    #         wilcoxon_results_adjusted.append({"Wilcoxon Statistic": None, "p-value": None, "Error": str(e)})


    # # Convert to DataFrame for clarity
    # results_df = pd.DataFrame(wilcoxon_results_adjusted, index=[
    #     "Tug of War vs Magnetic Attraction vs Toy Car on Ramp",
    #     "Solar System as Clockwork vs Sky as Clock",
    #     "Solid as Symphony Orchestra vs Ice Melting as Popsicle Melting",
    #     "SDLC as Plant Life Cycle vs Butterfly Life Cycle as Story",
    #     "Energy Flow as Water Pipes vs Heating Pan as Passing Torch",
    #     "Ecosystem as Computer Network vs Ecosystem as Web",
    #     "Cell as Biological Factory vs Cell as Factory",
    #     "Forces & Motion as Symphony Orchestra vs Path of Soccer Ball",
    #     "Earth as High-Tech Computer vs Earth Layers as Hard-Boiled Egg",
    #     "Photosynthesis as Solar-Powered Factory vs Plant as Solar Panel",
    #     "Periodic Table as City Map vs Periodic Table as Family Reunion",
    #     "DNA as Computer Code vs DNA as Recipe Book",
    #     "Climate as Complex Computer System vs Greenhouse Gases as Blanket",
    #     "Limits as Camera Zoom vs Limits as Zooming on Curve",
    #     "Uncertainty Principle as Blurry Photo vs Electrons as Student Decisions",
    #     "Thermodynamics as Budget vs Engine as Chef",
    #     "Deep Learning as Neural Network vs Training AI as Teaching Child",
    # ])

    # # Display results
    # results_df.to_csv("wilcoxon_results.csv")

    
    
    
#     data = {
#     "Educational Level": [
#         "Grade K", "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5",
#         "Grade 6", "Grade 7", "Grade 8",
#         "Grade 9", "Grade 10", "Grade 11", "Grade 12",
#         "Freshman Year", "Sophomore Year", "Junior Year", "Senior Year"
#     ],
#     "Concept": [
#         "Push and Pull", "Patterns in the Sky", "States of Matter", "Life Cycles of Plants and Animals",
#         "Energy Transfer", "Ecosystem Interactions", "Cell Theory", "Forces and Motion", "Earth’s Layers",
#         "Photosynthesis", "Periodic Table Trends", "DNA and Genetic Information", "Climate Change",
#         "Calculus and Limits", "Quantum Mechanics", "Thermodynamics Laws", "Artificial Intelligence"
#     ],
#     "Analogies": [
#         "Imagine a toy car on a ramp—the harder you push, the faster it moves.",
#         "Think of the sky as a giant clock, with celestial bodies as its moving hands.",
#         "Ice turning to water is like a popsicle melting on a hot summer day.",
#         "A butterfly’s life is like a story with four chapters: egg, caterpillar, chrysalis, and butterfly.",
#         "Heating a pan is like passing a torch, where energy moves from fire to the metal.",
#         "An ecosystem is like a web; tugging one thread affects the entire structure.",
#         "A cell is like a factory, with each part (organelle) having a specific job.",
#         "A soccer ball’s path depends on how and where it’s kicked.",
#         "Earth is like a hard-boiled egg: the shell is the crust, the egg white is the mantle, and the yolk is the core.",
#         "A plant is like a solar panel, turning sunlight into usable energy.",
#         "The periodic table is like a family reunion, where elements group by similar traits.",
#         "DNA is like a recipe book, with instructions for making proteins (the body's building blocks).",
#         "Burning fossil fuels is like wrapping Earth in a thicker blanket, trapping heat.",
#         "A limit is like zooming in on a curve to see its behavior more closely.",
#         "An electron is like a student deciding whether to act as a particle (being in one place) or a wave (spread out everywhere).",
#         "A car engine is like a chef, taking ingredients (fuel) and transforming them into motion (work).",
#         "Training AI is like teaching a child—it learns patterns and improves with practice."
#     ]}
#     new_analogies = [
#     {
#         "Analogy": "Tug of War vs. Magnetic Attraction",
#         "Explanation": "**Tug of War vs. Magnetic Attraction**\n   - In a game of tug of war, two teams pull on opposite ends of a rope, each trying to draw the other team towards them. This is analogous to magnetic attraction, where two magnets pull towards each other due to their opposite poles. In both scenarios, the force exerted is a pull, aiming to bring the opposing side closer.\n   - The tug of war represents a clear visual of forces in action, with each team exerting a pull force. Similarly, in magnetism, the invisible lines of force act to pull the magnets together. This analogy helps students visualize the concept of pull in a tangible way.\n   - The causal relationship here is the force exerted by each team or magnet, which determines the movement of the rope or the magnets. The stronger the force, the more likely one side will move towards the other, illustrating the principle of force and motion."
#     },
#     {
#         "Analogy": "The Solar System as a Clockwork Mechanism",
#         "Explanation": "**The Solar System as a Clockwork Mechanism**: Imagine the solar system as a grand clockwork mechanism, where each planet is a gear moving in perfect harmony. Just as gears in a clock are interconnected and driven by a central force, the planets orbit the Sun, influenced by gravitational forces. This analogy helps illustrate Kepler's laws of planetary motion, where the elliptical orbits and the harmonious relationship between orbital periods and distances mirror the precision of a well-crafted timepiece. The clockwork analogy emphasizes the predictability and regularity of celestial mechanics, akin to the ticking of a clock, where each tick represents the passage of time and the movement of planets in their orbits. This analogy can be expanded by considering how disruptions in the clockwork, such as a broken gear, can parallel gravitational perturbations affecting planetary orbits, offering a deeper understanding of celestial dynamics."
#     },
#     {
#         "Analogy": "Solid as a Symphony Orchestra",
#         "Explanation": "**Solid as a Symphony Orchestra**: \nImagine a symphony orchestra, where each musician plays their part in perfect harmony, following the conductor's lead. In a solid, atoms are like musicians in this orchestra, arranged in a precise, orderly fashion. Each atom has a specific position and role, contributing to the overall structure and stability of the solid. Just as the orchestra produces a cohesive sound, the atoms in a solid create a rigid structure with defined shape and volume. This analogy helps illustrate the concept of crystalline solids, where long-range order is paramount, much like the synchronized performance of an orchestra. The analogy extends to amorphous solids, akin to a less structured ensemble, where musicians play without a strict arrangement, resulting in a more fluid and less predictable performance."
#     },
#     {
#         "Analogy": "Software Development Lifecycle and Plant Life Cycles",
#         "Explanation": "**Software Development Lifecycle and Plant Life Cycles**: \n   - Just as software development follows a lifecycle from planning to deployment, plants undergo a series of stages from seed germination to maturity. In software, the planning phase is akin to seed germination, where the foundation is laid. The development phase parallels the growth of the plant, where the code (or plant) is nurtured and developed. Testing and deployment are similar to the flowering and fruiting stages, where the final product is ready for use or reproduction.\n   - This analogy helps students understand the sequential nature of plant life cycles, emphasizing the importance of each stage in achieving the final outcome. It also highlights the iterative nature of both processes, where feedback and adaptation are crucial for success.\n   - By comparing plant life cycles to software development, students can appreciate the complexity and interdependence of biological processes, much like the intricate steps involved in creating a functional software product."
#     },
#     {
#         "Analogy": "Energy Transfer as Water in Pipes",
#         "Explanation": "**Energy Transfer as Water in Pipes**: Imagine a network of pipes carrying water from one location to another. The water represents energy, and the pipes symbolize the pathways through which energy is transferred. Just as water flows from high pressure to low pressure, energy moves from areas of high concentration to low concentration. The efficiency of this transfer depends on the condition of the pipes and the presence of any obstacles or leaks.\n\nThis analogy is particularly useful for understanding conduction and convection. In conduction, energy moves through a solid material, similar to water flowing through a pipe. The thermal conductivity of the material is like the diameter of the pipe, determining how easily energy can flow. In convection, the movement of fluid carries energy, akin to water being pumped through the pipes. The flow rate and turbulence of the fluid affect the efficiency of energy transfer, much like the speed and pressure of the water.\n\nThe pipe analogy also illustrates the concept of resistance in energy transfer. Just as friction and blockages can impede water flow, resistance in a material can hinder energy transfer. This understanding is crucial for designing efficient systems, such as heat exchangers and thermal insulators."
#     },
#     {
#         "Analogy": "Ecosystem as a Computer Network",
#         "Explanation": "**Ecosystem as a Computer Network**: \nImagine an ecosystem as a vast computer network. In this network, each organism is a node, and the connections between them represent the interactions. Just as data packets travel through a network, energy and nutrients flow through the ecosystem. The network's efficiency depends on the robustness of these connections, much like how an ecosystem's health relies on the strength of its interactions. In both systems, disruptions can lead to cascading failures, highlighting the importance of maintaining balance and connectivity.\n\nIn a computer network, nodes communicate to perform tasks, share resources, and maintain system integrity. Similarly, in an ecosystem, organisms interact to exchange energy, recycle nutrients, and support biodiversity. Both systems require a balance of inputs and outputs to function optimally. For instance, if a key node in a network fails, it can disrupt communication, just as the loss of a keystone species can destabilize an ecosystem."
#     },
#     {
#         "Analogy": "Cells as Biological Factories",
#         "Explanation": "**Cells as Biological Factories**: Consider a factory, bustling with activity, where raw materials are transformed into finished products. Each section of the factory has a specific role, from assembly lines to quality control. Similarly, cells function as biological factories, where various organelles work together to produce the necessary components for life. The nucleus acts as the control center, directing operations, while the mitochondria generate energy, akin to the power supply of a factory.\n\nThis analogy illustrates the complexity and organization within a cell. Just as a factory relies on different departments to function efficiently, a cell relies on its organelles to perform specific tasks. This helps students visualize the cell as a dynamic and organized entity, where each part has a distinct role in maintaining the cell's overall function."
#     },
#     {
#         "Analogy": "Forces and Motion as a Symphony Orchestra",
#         "Explanation": "**Forces and Motion as a Symphony Orchestra**\n   - Imagine a symphony orchestra where each musician represents a different force acting on an object. The conductor, akin to the net force, orchestrates the musicians to create harmonious music, much like how forces combine to produce motion. Each instrument's sound is analogous to the magnitude and direction of a force, contributing to the overall performance.\n   - In this analogy, the musicians' ability to play in sync represents the concept of equilibrium, where forces balance each other out, resulting in no net motion. When the conductor signals a change, it mirrors an external force acting on an object, altering its state of motion.\n   - This analogy helps students visualize how multiple forces interact, emphasizing the importance of direction and magnitude. It also highlights the role of net force in determining motion, akin to the conductor's influence on the orchestra's performance."
#     },
#     {
#         "Analogy": "Earth as a High-Tech Computer",
#         "Explanation": "**Earth as a High-Tech Computer**: Consider the Earth as a sophisticated computer system, where various components, such as hardware and software, work together to process information and produce outputs. In this system, greenhouse gases are akin to software bugs that disrupt normal operations, leading to unexpected outcomes like global warming. Climate models, similar to diagnostic tools, help identify and predict these disruptions, allowing for corrective actions.\n\nThis analogy emphasizes the complexity and interconnectivity of the Earth's climate system, where changes in one component can have cascading effects on others. Just as a computer system requires regular updates and maintenance to function optimally, the climate system needs continuous monitoring and intervention to address the impacts of climate change."
#     },
#     {
#         "Analogy": "Photosynthesis as a Solar-Powered Factory",
#         "Explanation": "**Photosynthesis as a Solar-Powered Factory**: Imagine a factory that runs entirely on solar energy. This factory takes in raw materials, processes them using solar power, and produces valuable products. In this analogy, the factory represents the plant, the solar panels are the chlorophyll molecules, and the products are glucose and oxygen. Just like a factory, photosynthesis involves multiple stages and processes, each with a specific role in the overall production line. The light reactions are akin to the initial energy capture and conversion phase, where sunlight is harnessed to generate ATP and NADPH, the energy currency of the cell. These energy molecules are then used in the Calvin Cycle, similar to how a factory uses electricity to power its machinery, to convert carbon dioxide into glucose, the final product. This analogy helps students visualize the complex interplay of energy capture, conversion, and utilization in photosynthesis."
#     },
#     {
#         "Analogy": "Periodic Table as a City Map",
#         "Explanation": "**Periodic Table as a City Map**: Imagine the periodic table as a sprawling city map. Each element is like a neighborhood, with its own unique characteristics and residents (electrons). Just as neighborhoods are organized by streets and avenues, elements are organized by periods and groups. The atomic number is akin to a street address, pinpointing the exact location of an element in this city. As you move across a period (a street), the neighborhoods become more densely packed, representing the decreasing atomic radius. Moving down a group (an avenue), the neighborhoods expand, symbolizing the increasing atomic radius due to additional electron shells. This city map analogy helps students visualize the systematic organization of elements and the trends that emerge as one navigates through the periodic table."
#     },
#     {
#         "Analogy": "DNA as a Computer Code",
#         "Explanation": "**DNA as a Computer Code**: Consider DNA as a sophisticated computer code, where the sequence of nucleotides (A, T, C, G) represents lines of code that instruct the cell on how to function. Just as a computer program runs based on its code, cells operate based on the genetic instructions encoded in DNA. Mutations in DNA can be likened to bugs in a program, which can lead to errors or changes in function. This analogy highlights the precision and logic inherent in genetic information, drawing parallels to the digital world that students are familiar with, and underscores the importance of accurate coding for proper cellular function."
#     },
#     {
#         "Analogy": "Earth's Climate as a Complex Computer System",
#         "Explanation": "**Earth's Climate as a Complex Computer System**: Consider the Earth's climate as a sophisticated computer system, where various components, such as hardware and software, work together to process information and produce outputs. In this system, greenhouse gases are akin to software bugs that disrupt normal operations, leading to unexpected outcomes like global warming. Climate models, similar to diagnostic tools, help identify and predict these disruptions, allowing for corrective actions.\n\nThis analogy emphasizes the complexity and interconnectivity of the Earth's climate system, where changes in one component can have cascading effects on others. Just as a computer system requires regular updates and maintenance to function optimally, the climate system needs continuous monitoring and intervention to address the impacts of climate change."
#     },
#     {
#         "Analogy": "Limits as a Camera Zoom",
#         "Explanation": "**Limits as a Camera Zoom**: Imagine using a camera with a zoom lens to capture a distant object. As you zoom in, the object becomes clearer and more detailed. Similarly, limits in calculus allow you to \"zoom in\" on a function's behavior at a specific point, revealing its precise value or trend. Just as a camera lens focuses on a particular area, limits focus on a particular point, providing clarity and understanding of the function's behavior."
#     },
#     {
#         "Analogy": "Uncertainty Principle as a Blurry Photograph",
#         "Explanation": "**Uncertainty Principle as a Blurry Photograph**: Consider trying to take a photograph of a fast-moving object, like a speeding car. If the shutter speed of your camera is too slow, the image will be blurry, making it difficult to determine the car's exact position and speed simultaneously. This scenario is analogous to the Heisenberg Uncertainty Principle in quantum mechanics, which states that certain pairs of physical properties, such as position and momentum, cannot be precisely measured at the same time."
#     },
#     {
#         "Analogy": "First Law of Thermodynamics as a Financial Budget",
#         "Explanation": "**First Law of Thermodynamics: Financial Budget Analogy**: Consider a financial budget where money is neither created nor destroyed, only transferred between accounts. You might receive a paycheck (energy input), pay bills (energy output), and save the rest (internal energy change). This mirrors the First Law of Thermodynamics, which states that energy cannot be created or destroyed, only transformed."
#     },
#     {
#         "Analogy": "Deep Learning as a Brain's Neural Network",
#         "Explanation": "**Deep Learning as a Brain's Neural Network**: \nDeep learning can be likened to the intricate network of neurons in the human brain. Just as neurons in the brain communicate through synapses to process information, deep learning models use layers of artificial neurons to analyze data. Each layer in a neural network extracts different features, similar to how different brain regions specialize in processing various types of information. This analogy highlights the complexity and depth of deep learning models, which can capture intricate patterns in data. It also underscores the concept of learning through experience, as neural networks adjust their weights based on input data, much like the brain adapts through learning."
#     }
#     ]
#     eval_ours = []
#     eval_baseline = []
#     for i in range(len(new_analogies)):
#         eval_ours.append(evaluate_analogy_new(new_analogies[i].get("Analogy"), data.get("Concept")[i]))
#         eval_baseline.append(evaluate_analogy_new(data.get("Analogies")[i], data.get("Concept")[i]))
    
#     print(eval_ours)
#     print(eval_baseline)
#     # df = pd.DataFrame(data)
#     # df["AnalogyBSide"] = ""
#     # df["Evaluation"] = ""
#     # for i in range(len(df["Concept"])):
#     #     analogy, eval_res = main(df["Concept"][i])
#     #     df.at[i, "AnalogyBSide"] = analogy  # Use df.at for assignment
#     #     df.at[i, "Evaluation"] = eval_res

#     # #df["AnalogyBSide"] = df["Concept"].apply(main)
#     # import ace_tools as tools; tools.display_dataframe_to_user(name="STEM Concepts and Analogies", dataframe=df)
#     #create_table(data)



