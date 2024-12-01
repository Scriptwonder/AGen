from flask import Flask, request, jsonify
from flask_cors import CORS
import analogyGen as AnalogyGen

app = Flask(__name__)

CORS(app)

@app.route('/generate-analogy', methods=['POST'])
def generate_analogy():
    data = request.json
    concept = data.get('concept')
    # Add your analogy generation logic here
    concept, summary, knowledge_graph = AnalogyGen.concept_gen(concept)
    response = {
        "concept": concept,
        "summary": summary,
        "knowledge_graph": parse_triplets(knowledge_graph)
    }
    print(response)
    return jsonify(response)

def parse_triplets(graph_text):
    # Parses the knowledge graph string into a list of dictionaries representing triplets
    triplets = []
    for line in graph_text.split('\n'):
        if line.strip():
            source, relation, target = line.strip().split(',')
            triplets.append({
                "source": source.strip(),
                "relation": relation.strip(),
                "target": target.strip()
            })
    return triplets

if __name__ == "__main__":
    app.run(debug=True)