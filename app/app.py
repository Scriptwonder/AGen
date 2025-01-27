from flask import Flask, request, jsonify
from flask_cors import CORS
import analogyGen as AnalogyGen
import conceptGraphGen as ConceptGen
import json 

app = Flask(__name__)

CORS(app)

@app.route('/generate-concept', methods=['POST'])
def generate_concept():
    data = request.json
    concept = data.get('concept', '')
    # Add your analogy generation logic here
    concept, summary, knowledge_graph = AnalogyGen.concept_gen(concept)
    core_concept = AnalogyGen.generate_core_meanings(concept)
    
    response = {
        "concept": concept,
        "summary": summary,
        "knowledge_graph": parse_triplets(knowledge_graph),
        "core_concept": core_concept
    }
    print(response)
    return jsonify(response)

@app.route('/get-graph', methods=['POST'])
def get_graph():
    data = request.get_json()
    concept = data.get('concept') # Parse input
    bg = data.get('bg')

    graph_data= ConceptGen.main(concept, bg)
    return jsonify(graph_data)

@app.route('/generate-analogy-graph', methods=['POST'])
def generate_analogy_graph():
    data = request.get_json()
    
    graph_data = ConceptGen.generate_analogy_graphs_new()
    return jsonify(graph_data)



@app.route('/generate-analogy', methods=['POST'])
def generate_analogy():
    data = request.json
    concept = data.get('concept', '')
    audience = data.get('audience', '')
    if not concept:
        return jsonify({"error": "Concept is required"}), 400

    try:
        # Generate analogies
        #analogies, explanations, evaluations, sprompts = AnalogyGen.analogy_gen(concept)
        print(1)
        analogies, explanations, evaluations, images = ConceptGen.main(concept, audience)
        
        print(analogies)
        print(explanations)
        print(evaluations)
        print(images)
        # Combine results with image generation
        analogy_results = []
        for i in range(len(analogies)):
            analogy_results.append({
                "analogy": analogies[i],
                "explanation": explanations[i],
                "evaluation": evaluations[i],
                "image_url": images[i]
            })
        print("This step is fine")
        return jsonify({"analogies": analogy_results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @app.route('/generate-analogy', methods=['POST'])
# def generate_analogy():
#     data = request.get_json()
#     bg = data.get('bg')

#     # Generate analogies for the concept
#     analogy_results, analogy_summaries, analogy_kgs, analogy_terminologies = AnalogyGen.analogy_gen(bg)  # Assuming this function generates analogies as well

#     print(analogy_kgs)
#     # Prepare the response
#     response = {
#         "analogies_concepts": analogy_results,
#         "analogies_summaries": analogy_summaries,
#         "analogies_kgs": [parse_triplets(kg) for kg in analogy_kgs],
#         "analogies_terminologies": analogy_terminologies
#         #"analogies_score": eval_score
#     }
#     print(response)

#     return jsonify(response)

@app.route('/calculate-similarity', methods=['POST'])
def calculate_similarity():
    data = request.get_json()
    #concept_graph = data.get('concept_graph')
    #analogy_graph = data.get('analogy_graph')
    analogy_index = data.get('analogy_index')

    # Calculate structure similarity
    similarity = AnalogyGen.calculate_graph_edit_distance_by_index(analogy_index)  # Assuming this function calculates the similarity between two graphs
    print(similarity)
    # Prepare the response
    response = {
        "similarity_score": similarity
    }

    return jsonify(response)

def parse_triplets(graph_text):
    # Parses the knowledge graph string into a list of dictionaries representing triplets
    triplets = []
    for line in graph_text.split('\n'):
        if line.strip():
            parts = line.strip().split(',')
            if len(parts) == 3:
                source, relation, target = parts
                triplets.append({
                    "source": source.strip(),
                    "relation": relation.strip(),
                    "target": target.strip()
                })
            else:
                print(f"Invalid triplet: {line}")
    return triplets



if __name__ == "__main__":
    app.run(debug=True)