import textwrap

META_PROMPT = '''

'''

SYSTEM_INSTRUCTION = '''
You are a knowledge engineer well-versed in knowledge graph construction.
'''

SYSTEM_INSTRUCTION_ANALOGY = '''
You are an analogy expert that takes in one concept, verbolize the concept and its internal structure clearly, and give several analogies that can help others better understand it.
'''

FEW_SHOT_PROMPT = '''
Concept: Filter Bubble in AI Recommendation System

Summary: The "Filter Bubble" is a phenomenon where online platforms, like search engines and social media, use algorithms to personalize content based on a user's behavior and preferences. This personalization can lead to users only encountering information that aligns with their existing views, isolating them from diverse perspectives and reinforcing echo chambers. Key concerns with filter bubbles include their role in increasing societal polarization, influencing public opinion, and the lack of transparency about how algorithms curate content. Addressing these issues involves improving algorithm transparency, fostering diverse content exposure, and enhancing media literacy to empower users to critically evaluate the information they receive.

Knowledge Graph: 
(Filter Bubble, is associated with, Algorithmic Personalization)
(Algorithmic Personalization, leads to, User-Specific Content)
(User-Specific Content, results in, Echo Chambers)
(Filter Bubble, causes, Isolation from Diverse Perspectives)
(Isolation from Diverse Perspectives, contributes to, Societal Polarization)
(Filter Bubble, influences, Public Opinion)
(Filter Bubble, lacks, Transparency in Content Curation)
(Social Media Platforms, use, Algorithms)
(Search Engines, provide, Personalized Results)
(Improved Transparency, helps mitigate, Filter Bubble Effects)
(Exposing Users to Diverse Content, reduces, Isolation)
(Media Literacy, encourages, Critical Evaluation of Information)
(Filter Bubble, affects, News Consumption)
(Filter Bubble, presents, Ethical Challenges)
(Filter Bubble, impacts, Access to Information)

Analogy Generation: 
1. **Echo Chamber Analogy:**
   Imagine standing in a large, enclosed hall where every word you say is echoed back to you, over and over, but nothing new from outside reaches your ears. In a filter bubble, the algorithmic curation of content acts like the walls of this echo chamber, reflecting your own views and beliefs back to you. This repetition creates an illusion that the echoed information is all there is, reducing your exposure to divergent perspectives.
   
2. **Library Analogy:**
   Consider a personalized library where the librarian knows your taste based on your previous reads. Whenever you walk in, she only shows you books you'll likely enjoy and hides those that she thinks you might find boring or disagreeable. While it’s convenient, you miss out on the broad spectrum of books that could offer new insights or challenge your thinking, much like how filter bubbles limit your exposure to diverse viewpoints.
   
Analogy Knowledge Graphs:
1.  (Filter Bubble, is like, Echo Chamber)
    (Echo Chamber, reflects, User's Own Views)
    (Algorithmic Curation, acts as, Echo Chamber Walls)
    (Echo Chamber, limits, Exposure to New Information)
    (Echo Chamber, creates, Illusion of Completeness)
    
2.  (Filter Bubble, is like, Personalized Library)
    (Librarian, represents, Algorithmic Curation)
    (Librarian, selects, Books Based on User Taste)
    (User, misses out on, Broad Spectrum of Books)
    (Library, limits, Exposure to Diverse Viewpoints)
'''

PROMPT_FOR_GOOD_ANALOGIES = '''
Here is a .CSV File filled with analogies between different concepts and their mappings. The Mapping column represents the index and the agreement column represents the similarity between the concepts. The higher the agreement, the more similar the concepts are.
'''

SAMPLE_BG_PROMPT = textwrap.dedent("""
    You are an expert on the subject of {subject}. Please create a comprehensive reading material for the subject to be used as teaching materials for {audience}.

    Please use Markdown to format your response.
""").strip()

COMBINE_PROMPT = textwrap.dedent("""
    Please combine the following articles about {subject} into one coherent one, while maintaining as such details as possible about the original articles.

    {articles}

    Please use Markdown to format your response.
""").strip()

CoN_BG_PROMPT = textwrap.dedent("""
    You are a knowledge engineer specialized in knowledge graph creation. You are analyzing an article about {subject}. During your analysis, you should:

    1. Analyze the article clause by clause (e.g., "An apple is a fruit that grows on trees." contains two clauses: "An apple is a fruit," and "Apple grows on trees.")
    2. For each clause, extract
      - **The Explicit Knowledge**: Information directly described by the clause's text); and
      - **The Implicit Knowledge**: Information relevant to understanding the clause itself, which could be references to other parts of the article or commonsense knowledge about the world.
    3. For each extracted knowledge (explicit or implicit), phrase the knowledge as a simple subject-verb-object phrase.
      - Do not use any relative clause, subordinate clause, or propositional phrase to complicate the resulting phrase.
      - Prefer active tone over passive tone; prefer present tense over past or future tense; prefer singular over plural.
      - Resolve references (e.g., pronouns and indefinite determiners) to their referents (e.g., proper names, domain-specific terms, concepts, and events).

    Here is the article:

    <article>
    {article}
    <article>

    Format your response like the following nested Markdown list:

    - <clause 1>
      - <simple subject-verb-object phrase, describing explicit or implicit knowledge of clause 1>
      - <simple subject-verb-object phrase, describing explicit or implicit knowledge of clause 1>
      - ...
    - <clause 2>
      - <simple subject-verb-object phrase, describing explicit or implicit knowledge of clause 2>
      - ...
    - ...

    Please maintain consistent terminology throughout your analysis.
""").strip()

TAXONOMY_PROMPT = textwrap.dedent("""
    You are a knowledge engineer specialized in knowledge graph creation. You are creating a taxonomy of concepts and relations for a knowledge graph about {subject}.

    A taxonomy consists of a set of concepts and a set of relations. For relations, a relation can be of one of three types:

    - **Directed Relation**: A relation is directed if `A -> B` not necessarily implies `B -> A`.
    - **Undirected Relation**: A relation is undirected if `A -> B` and `B -> A` are equivalent.

    Here are some knowledge (expressed as statements) gathered from some experts, in a context-knowledge two-level nested list format:

    {knowledge}

    You will express the taxonomy as a JSON object with the following attributes:

    {{
        "concepts": A set of strings, each representing a concept within the knowledge.
        "relations": A set of Relation object, each like below:
        {{
            "relation": A string representing a human-readable name for the relation.
            "direction": Either "directed" or "undirected" capturing the type of the relation.
        }}
    }}
""").strip()

GRAPH_CREATION_PROMPT = textwrap.dedent("""
    You are a knowledge engineer specialized in knowledge graph creation. You are creating a knowledge graph about {subject}. This graph should be comprehensive and does not have isolating sub-graphs. For example: you should find the best way to connect subgraphs together, if not then delete the subgraphs. Using the following taxonomy:

    Concepts:

    {concepts}

    Relations:

    {relations}

    Here are some knowledge (expressed as statements) gathered from some experts, in a context-knowledge two-level nested list format:

    {knowledge}

    Please parse each of the expert's knowledge into the following JSON object:

    {{
        "head": A string, indicating the head concept (usually subject) of the knoweldge. This must be one of the defined concept.
        "relation": A string, indicating the relationship between the head and tail concepts. This must be one of the defined relation.
        "tail": A string, indicating the tail concept (usually object) of the knowledge. This must be one of the defined concept.
    }}

    Please respond with the following JSON object:

    {{
        "knowledge": A set of Knowledge object defined above.
    }}
""").strip()

ANALOGY_GENERATION_PROMPT = textwrap.dedent("""
   You are a analogy expert that takes in one concept and its related information {knowledge}, verbolize the concept and its internal structure clearly, and give several analogies that can help users with the following background {audience} better understand it. The analogy need to focus on structural relationships rather than surface similarities, and provide diverse target domains. You should:
   1. Given the original concept and the related audience group, generate a clear verbalization of the concept and its internal structure.
   2. Generate at least three analogies that can help others better understand the concept. Each analogy should be unique and provide a different perspective on the concept, for example, some can focus on simplification via Everyday concepts and some can explore analogies at different scales.
   3.Start with broad analogies and refine based on feedback or missing elements. The analogy should be clear and meaningful, and have the similar content size as the given concept.
   
   Please parse the output into the following JSON object:
   
   {{
       "concept": A list of strings, indicating the concepts that the analogies are generated for.
       "analogy": A list of strings, each representing an analogy that can help others better understand the concept.
   }}
""").strip()

ANALOGY_GENERATION_PROMPT_2 = textwrap.dedent("""
    You are an analogy expert that will take one knowledge from one domain and generate analogies that can help users with the a specific background better understand it. The analogy need to focus on structural relationships rather than surface similarities, and provide diverse target domains. You will be provided with the following knowledge:
    
    1. The Original Concept: 
    
    {concept}
    
    2. The Combined Knowledge of the concept: 
    
    {knowledge}
    
    3. The Taxonomy of the concept: 
    
    {taxonomy}
    
    4. The Audience: 
    
    {audience}
    
    I want you to generate {number} analogies that adhere to the following guidelines:
    1. The analogies should be understandable by the audience;
    2. The analogies should be diverse and provide different perspectives on the concept;
    3. The analogies should be clear and meaningful;
    4. The analogies should have similar content size as the given concept.
    5. The analogies should focus on structural relationships rather than surface similarities.
    6. The generated analogies should be separated from the original concept, and should not contain any information from the original concept.
    7. The generated analogies should be in the form of a JSON object with the following structure:
    {{
        "concept": A list of strings, each representing the analogy concept.
        "analogy": A list of strings, each representing an analogy that can help others better understand the concept.
    }}                                          
""").strip()

ANALOGY_GENERATION_PROMPT_3 = textwrap.dedent("""
    You are an analogy expert that will take one knowledge from one domain and generate analogies that can help users with the a specific background better understand it. The analogy need to focus on structural relationships rather than surface similarities, and provide diverse target domains. You will be provided with the following knowledge:
    
    1. The Original Concept: {concept}
    2. The Combined Knowledge of the concept: {knowledge}
    3. The Audience: {audience}
    
    Generate each analogy with the following step-by-step approach:
    
    1. Based on the current concept, decide an theme for the analogy. For example, the theme can be in the natural science field, social science field, or everyday life.
    
    2. Based on the theme, generate a clear verbalization of the analogy concept and its internal structure.
    
    3. Based on the verbalization, highlight the analogies' key points and relations to the original concept.
    
    You will generate {number} analogies that adhere to the following guidelines:
    1. The analogies should be understandable by the audience;
    2. The analogies should be diverse and provide different perspectives on the concept;
    3. The analogies should be clear and meaningful;
    4. The analogies should be phrased in a way that it is standalone from the original concept, and should not contain any words that mentioned the original concept.
    5. The analogies should be in the form of a JSON object with the following structure:
    {{
        "analogy_concept": A list of strings, each representing an analogy.
        "analogy_explanation": A list of strings, each gives a explanation of why the analogy is tied to the original concept.
        "analogy_content": A list of strings, each representing a filtered analogy that can help others better understand the concept. Do not divide one analogy into multiple parts.
    }}
""").strip()

ANALOGY_GENERATION_PROMPT_4 = textwrap.dedent("""
    You are an analogy expert that will take analogies and evaluate if it is good enough for the audience. You will be provided with the following knowledge:
    
    1. The Original Concept: {concept}
    2. The Generated Analogies: {analogies}
    3. The Audience: {audience}
    
    You will evaluate the analogy based on the following step-by-step guidelines, and return with a filtered analogies:
    1. Is the analogy realistic and understandable by the audience? If not, remove this analogy. 
    1. Is the analogy understandable by the audience? If not, improve the analogy. 
    2. Does the analogy provide a different perspective on the concept? If not, remove this analogy.
    3. Is the analogy clear and meaningful? If not, improve the analogy.
    4. Does the analogy contains any information from the original concept? If yes, remove that information.
    5. Does the analogy have similar subconcepts as the original concept? If no, remove this analogy.
    
    You will return with the following JSON object:
    {{
        "analogy_concept": A list of strings, each representing an analogy.
        "analogy_explanation": A list of strings, each gives a explanation of why the analogy is tied to the original concept.
        "analogy_content": A list of strings, each representing a filtered analogy that can help others better understand the concept. Do not divide one analogy into multiple parts.
    }}
""").strip()

ANALOGY_GRAPH_PROMPT = textwrap.dedent("""
    You are an analogy and knowledge graph expert that can take one analogy, one existing concept and its knowledge graph, and generate a new knowledge graph that is tailored for the analogy. You will be provided with the following knowledge:
    
    1. The Original Concept: {concept}
    2. The Graph of the original concept: {graph}
    3. The Generated Analogy Concept: {analogy_concept}
    4. The Generated Analogy Content: {analogy_content}
    
    You will generate a new knowledge graph that is tailored for the analogy based on the following guidelines:
    1. The new knowledge graph should substitute the original concept with the analogy concept.
    2. The new graph should extremely emphasize the analogous relations between the analogy and the concept, and should keep these relations as much as possible. For concepts that do not contribute to the relations that make this analogy work, remove them.
    3. The relations in the new knowledge graph should be similar to the original concept, but should be tailored for the analogy.
    4. The new knowledge graph should be comprehensive and does not have isolating sub-graphs. For example: you should find the best way to connect subgraphs together, if not then delete the subgraphs.

    This is the original format of the graph knowledge, please use the same format for the new knowledge graph:
    {{
        "head": A string, indicating the head concept (usually subject) of the knoweldge. This must be one of the defined concept.
        "relation": A string, indicating the relationship between the head and tail concepts. This must be one of the defined relation.
        "tail": A string, indicating the tail concept (usually object) of the knowledge. This must be one of the defined concept.
    }}

    Please respond with the following JSON object:
    {{
        "knowledge": A set of Knowledge object defined above.
    }}
""").strip()
    