import spacy
from collections import defaultdict

nlp = spacy.load("en_core_web_md")

def normalize_entity(entity, entity_map):
    """Normalize an entity by checking if it's similar to existing mapped entities."""
    for canonical_entity in entity_map:
        if nlp(entity).similarity(nlp(canonical_entity)) > 0.8:
            return canonical_entity
    entity_map[entity] = entity
    return entity

def normalize_triplets(triplets):
    """Normalize entities and relations in the triplets."""
    entity_map = {}
    normalized_triplets = []

    for source, relation, target in triplets:
        norm_source = normalize_entity(source, entity_map)
        norm_target = normalize_entity(target, entity_map)
        normalized_triplets.append((norm_source, relation.lower(), norm_target))
    
    return normalized_triplets

def parse_triplets(graph_text):
    # Parses the knowledge graph string into a list of dictionaries representing triplets
    triplets = []
    for line in graph_text.split('\n'):
        if line.strip():
            parts = line.strip().split(',')
            if len(parts) == 3:
                source, relation, target = parts
                triplets.append({
                    source.strip(),
                    relation.strip(),
                    target.strip()
                })
            else:
                print(f"Invalid triplet: {line}")
    return triplets

def combine_triplets(triplet_sets):
    """Combine multiple sets of triplets into one comprehensive set."""
    # Step 1: Normalize all triplets
    all_triplets = []
    for triplets in triplet_sets:
        parsed = parse_triplets(triplets)
        normalized = normalize_triplets(parsed)
        all_triplets.extend(normalized)

    # Step 2: Create a set of unique triplets
    unique_triplets = set(all_triplets)

    return list(unique_triplets)

def prioritize_triplets(triplet_sets):
    """Assign scores to each triplet and retain the most informative ones."""
    triplet_frequency = defaultdict(int)

    # Step 1: Count the frequency of each triplet
    for triplets in triplet_sets:
        for triplet in triplets:
            triplet_frequency[triplet] += 1

    # Step 2: Set a threshold for frequency to determine importance
    threshold = len(triplet_sets) // 2  # Triplets that occur in at least half of the sets are prioritized

    # Step 3: Filter out triplets that do not meet the threshold
    prioritized_triplets = [triplet for triplet, count in triplet_frequency.items() if count > threshold]

    return prioritized_triplets

def construct_best_knowledge(triplet_sets):
    """Construct the best set of triplets by combining, normalizing, and prioritizing."""
    # Combine and normalize triplets
    combined_triplets = combine_triplets(triplet_sets)
    print (combined_triplets)

    # Prioritize triplets based on their frequency across sets
    best_knowledge_triplets = prioritize_triplets([combined_triplets])
    print (best_knowledge_triplets)

    return best_knowledge_triplets

# Example Usage
# if __name__ == '__main__':
#     triplet_set_1 = [("AI", "is a field of", "Computer Science"),
#                      ("Machine Learning", "is part of", "AI"),
#                      ("AI", "has applications in", "Healthcare")]
    
#     triplet_set_2 = [("Artificial Intelligence", "is a field of", "Computer Science"),
#                      ("Deep Learning", "is part of", "Machine Learning"),
#                      ("AI", "is used in", "Healthcare")]

#     triplet_set_3 = [("AI", "belongs to", "Computer Science"),
#                      ("AI", "is a field of", "Computer Science"),
#                      ("Machine Learning", "is part of", "AI"),
#                      ("ML", "is a subset of", "AI"),
#                      ("Artificial Intelligence", "impacts", "Healthcare")]

#     triplet_sets = [triplet_set_1, triplet_set_2, triplet_set_3]

#     best_knowledge = construct_best_knowledge(triplet_sets)
#     for triplet in best_knowledge:
#         print(triplet)
