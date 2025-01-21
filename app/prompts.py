import textwrap

#Benchmark from "https://aclanthology.org/2024.inlg-genchal.1/"
#Meaningful Analogy and Novelty for OAMN
EVALUATION_BENCHMARK_OAMN = textwrap.dedent("""
You will be given one piece of text written to explain a target concept. Your task is to rate the text on two metrics. Please make sure you read and understand these instructions carefully. Please keep this document open while reviewing, and refer to it as needed. Evaluation Criteria: Meaningful analogy (1-4) - Whether the given text is a meaningful (i.e., valid and correct) analogy, where, 1 means Strongly Disagree that text contains meaningful analogy, 2 means Somewhat Disagree that text contains meaningful analogy, 3 means Somewhat Agree that text contains meaningful analogy, 4 means Strongly Agree that text contains meaningful analogy. Some examples of text that is not a meaningful analogy include the following cases: The text is not actually an analogy. It could be a definition, example, tautology, etc. The text contains little to no relevant information pertaining to the target concept. Important details about the analogous concepts are either incorrect or missing, or the provided explanation was insufficient, making the analogy completely wrong or weak at best. The text is completely incoherent or gramatically incorrect. Novelty (1-4) - How novel is the text, i.e., can similar text be found online? 1 means the same text (potentially paraphrased) is found on the web, 2 means similar text is found on the web, 3 means no similar text is found online but text is straightforward to infer from the content found online, 4 means no remotely similar text is found online and text is not straightforward to infer from the content found online. Evaluation Steps: 1. Read the given text carefully. 2. Assign a score on a scale of 1-4 for the meaningful analogy criteria. 3. Assign a score on a scale of 1-4 for the novelty criteria. Examples: Text: DNA replication can be thought of as a photocopier. The DNA molecule is like the original document, and each strand of DNA is like one copy of the document. During replication, the two strands are separated, and new copies of each strand are created. Evaluation Form:- Meaningful analogy: 4- Novelty: 1 Text: Breathing mechanism of frogs can be analogy to bellows of blacksmith. Just like bellows, the frog's lungs are inflated and deflated by muscles that run along either side of its ribcage. When the frog inhales, the muscles contract, pushing air into the lungs. When it exhales, the muscles relax and air is forced out. Evaluation Form:- Meaningful analogy: 4- Novelty: 4 Text: In computing, an operating system kernel is the core of a computer operating system. It is responsible for managing hardware and software resources and providing common services for application programs. The kernel performs its tasks in cooperation with device drivers, which are modules that load into the kernel to provide specific functions, such as access to the disk drive or network card. Evaluation Form:- Meaningful analogy: 1- Novelty: 1 ========================= Target: '{{Target}}' Text: {{Document}} Evaluation Form:
""").strip()

#For Structural Consistency
EVALUATION_BENCHMARK_MANAED = textwrap.dedent("""
You will be given one analogy written to explain a target concept. Your task is to rate the analogy on four metrics. Please make sure you read and understand these instructions carefully. Please keep this document open while reviewing, and refer to it as needed. Evaluation Criteria: Target Accuracy (1-4) - The accuracy of facts about the target concept. Penalize factually incorrect text about the target concept. Source Accuracy (1-4) - The accuracy of facts about the source concept. Penalize factually incorrect text about the source concept. If a separate source concept is not found (e.g., source concept is missing or the target concept is compared to itself), set this score to -1. Mapping Consistency (1-4) - Structural consistency of the mapping between source and target concepts. Penalize if the source concepts of the sub-analogies are disconneted (i.e., do not coherently consitute a single concept). Also, penalize if 1:1 mapping is not found in the sub-analogies (i.e., if the same source or target concept is used in multiple sub-analogies). Usefulness (1-4) - The usefulness of the analogy for explaining the concept. Evaluation Steps: 1. Read the analogy carefully and identify all the sub-analogies. 2. Read each sub-analogy and identify the target and source concept (the concept being compared to the target). 3. For each sub-analogy, write it and assign a score for its target accuracy on a scale of 1 to 4, where 1 is the lowest and 4 is the highest based on the Evaluation Criteria. 4. For each sub-analogy, write it and assign a score for its source accuracy on a scale of 1 to 4, where 1 is the lowest and 4 is the highest, or set it to -1 based on the Evaluation Criteria . 5. Assign a score for the overall mapping consistency on a scale of 1 to 4, where 1 is the lowest and 4 is the highest as per the Evaluation Criteria. 6. Assign a score for the overall usefulness on a scale of 1 to 4, where 1 is the lowest and 4 is the highest as per the Evaluation Criteria. Example: Analogy Text: The atmosphere is like a hug because it is warm and comforting. The thermosphere is like the top of a mountain because it is the highest point. The mesosphere is like the middle of a journey because it is the middle point. The troposphere is like the bottom of the ocean because it is the lowest point. Evaluation Form:- Sub-analogy 1: The atmosphere is like a hug because it is warm and comforting. - Source Accuracy: 4- Target Accuracy: 2- Sub-analogy 2: The thermosphere is like the top of a mountain because it is the highest point.- Source Accuracy: 4- Target Accuracy: 1- Sub-analogy 3: The mesosphere is like the middle of a journey because it is the middle point.- Source Accuracy: 4- Target Accuracy: 4- Sub-analogy 4: The troposphere is like the bottom of the ocean because it is the lowest point.- Source Accuracy: 4- Target Accuracy: 4- Mapping Consistency: 2- Usefulness: 3 ========================= Target: '{{Target}}' Analogy Text: {{Document}} Evaluation Form:- Sub-analogy 1
""").strip()

#For Usefulness
EVALUATION_BENCHMARK_USEFULNESS = textwrap.dedent("""
You will be given one analogy written to explain a target concept. Your task is to rate the analogy on one metric. Please make sure you read and understand these instructions carefully. Please keep this document open while reviewing, and refer to it as needed. Evaluation Criteria: Usefulness (1-4) - The usefulness of the analogy for explaining the concept. Evaluation Steps: 1. Read the analogy carefully. 2. Assign a score for the overall usefulness on a scale of 1 to 4, where 1 is the lowest and 4 is the highest as per the Evaluation Criteria. Example:  Analogy Text:  The atmosphere is like a hug because it is warm and comforting. The thermosphere is like the top of a mountain because it is the highest point. The mesosphere is like the middle of a journey because it is the middle point. The troposphere is like the bottom of the ocean because it is the lowest point. Evaluation Form:  - Usefulness: 3 ========================= Analogy Text: {{Document}} Evaluation Form: - Usefulness:
""").strip()

#source and target accuracy
EVALUATION_BENCHMARK_ACCURACY = textwrap.dedent("""
You will be given one analogy written to explain a target concept {concept}. Your task is to rate the analogy on four metrics. Please make sure you read and understand these instructions carefully. Please keep this document open while reviewing, and refer to it as needed. Evaluation Criteria: Source Accuracy {{-1, 1-4}} - The accuracy of facts about the source concept. Penalize factually incorrect text about the source concept. If a separate source concept is not found (e.g., source concept is missing or the target concept is compared to itself), set this score to -1. Target Accuracy (1-4) - The accuracy of facts about the target concept. Penalize factually incorrect text about the target concept. Evaluation Steps: 1. Read the analogy carefully. 2. Identify all facts related to the source concept (the concept being compared to the target). 3. Assign a score for its source accuracy on a scale of 1 to 4, where 1 is the lowest and 4 is the highest, or set it to -1 based on the Evaluation Criteria. 4. Read each sub-analogy and identify all facts related to the target concept. 5. Assign a score for the target accuracy on a scale of 1 to 4, where 1 is the lowest and 4 is the highest. Examples:  Analogy Text: The atmosphere is like a blanket because it surrounds and protects us. Evaluation Form:  - Source Accuracy (blanket): 4  - Target Accuracy (atmosphere): 4 Analogy Text: System software is like the sugar for a cake because it helps to sweeten the final product. Evaluation Form:  - Source Accuracy (sugar): 4  - Target Accuracy (system software): 1 Analogy Text: The moons are the cousins because they orbit the planets and are much smaller than the planets. Evaluation Form:  - Source Accuracy (cousins): 1  - Target Accuracy (moons): 4 ========================= Target: '{{Target}}' Analogy Text: {{Document}} Evaluation Form:
""").strip()

EVALUATION_COMBINATION_PROMPT = textwrap.dedent("""
You will be given a combination of analogy evaluations {evaluation} based on different criteria. Combine them together to be a concise evaluation of the analogy.
Keep all the core evaluations and remove any repeated evaluations and informations. Return the combined evaluation.
""").strip()                                                                                                 

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
    You are an expert on the subject of {subject}. Please create a comprehensive reading material for the subject to be used as teaching materials for {audience}. The Knowledge and material must be fit to the group's prior knowledge and cognitive level. 

    Please use Markdown to format your response.
""").strip()

COMBINE_PROMPT = textwrap.dedent("""
    Please combine the following articles about {subject} into one coherent one, while maintaining as such details as possible about the original articles. Make sure it fits into {audience}'s proir knowledge and cognitive level. Remove and Edit if needed.

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

ANALOGY_WARNING_PROMPT = textwrap.dedent("""
    You are an analogy expert that will take analogies and evaluate if it is good enough for the audience. First of all before you start, I want you to generate a standard/metric for evaluating analogies. What would be a good analogy and what would be a bad analogy objectively and subjectively? Take a step further, what would be analogies that this audience {audience} would learn most from? Please provide a detailed explanation of the standard/metric for evaluating analogies, and you will use that to generate analogies in the future.
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
    
ANALOGY_EVALUATION_PROMPT = textwrap.dedent("""
PROMPT:
You are an analogy evaluator. You will be given an analogy {analogy_concept} and its explanation {analogy_content} along with the original concept {origin} and asked to rate it on six dimensions, each on a scale of 1 (lowest) to 10 (highest), along with brief explanatory comments. These six dimensions are based on Gentner’s (2013) framework for analogical learning and reasoning:

1. Structural Alignment
   - How well does the analogy map the key relational structures (not just surface features) from the source to the target?
   - Score: 1 = Almost no meaningful relational parallel; 10 = Highly systematic, deep relational match.

2. Progressive Alignment Potential
   - Does this analogy allow for incremental or deeper exploration (start simple, then uncover more complex relations)?
   - Score: 1 = Not expandable; 10 = Easily supports step-by-step or more in-depth elaboration.

3. Commonalities & Differences
   - Does the analogy highlight both important shared relations and critical mismatches?
   - Score: 1 = Overlooks major gaps or mismatches; 10 = Explicitly clarifies parallels and limitations.

4. Abstraction Level & Learner Readiness
   - Is the analogy appropriate for the learner's background {audience} and pitched at a suitable level of abstraction?
   - Score: 1 = Mismatch with learners' needs; 10 = Perfect fit for their prior knowledge and cognitive level.

5. Clarity & Engagement (Comparison Focus)
   - Is the analogy presented clearly and engagingly, prompting an active comparison between source and target?
   - Score: 1 = Confusing or unengaging; 10 = Very clear, step-by-step mapping that hooks the learner’s interest.

6. Facilitation of Transfer & Deep Understanding
   - Does the analogy help learners transfer insights to new contexts or deepen overall comprehension?
   - Score: 1 = Provides no meaningful new understanding; 10 = Greatly enhances conceptual grasp and fosters transfer.

INSTRUCTIONS:
1. Read the provided analogy.
2. Filter or refine the analogy with the given guidelines:
    1. Is the analogy realistic and understandable by the audience {audience}? If not, remove this analogy. 
    1. Is the analogy understandable by the audience? If not, refine the analogy from the six dimensions.
    2. Does the analogy provide a different perspective on the concept? If not, remove this analogy.
    3. Is the analogy clear and meaningful? If not, refine the analogy from the six dimensions.
    4. Does the analogy contains any information from the original concept? If yes, remove that information.
    5. Does the analogy have similar subconcepts as the original concept? If no, remove this analogy.
2. With the updated Analogy, for each of the six dimensions, give a rating from 1–10.
3. Provide 1–3 sentences explaining why you assigned each rating.
4. Summarize the analogy’s overall effectiveness, and provide potential better alternatives.

FINAL OUTPUT FORMAT EXAMPLE:
{{
    "Analogy_Concept": "Filter Bubble",
    "Analogy_Content": "A Filter Bubble is a phenomenon where online platforms use algorithms to personalize content based on a user's behavior and preferences, leading to users only encountering information that aligns with their existing views.",
    "Dimensions": {{
        "StructuralAlignment": {{
            "score": 8,
            "comment": "Captures the main relational elements well, though a few secondary relations are missing."
        }},
        "ProgressiveAlignmentPotential": {{
            "score": 6,
            "comment": "Could be elaborated to highlight more causal sequences."
        }},
        "CommonalitiesAndDifferences": {{
            "score": 8,
            "comment": "Mentions a key mismatch, but could emphasize limitations further."
        }},
        "AbstractionLevelAndLearnerReadiness": {{
            "score": 10,
            "comment": "Perfectly aligns with the intended age group’s background."
        }},
        "ClarityAndEngagement": {{
            "score": 8,
            "comment": "Visually appealing, but would benefit from more explicit role-mapping."
        }},
        "FacilitationOfTransfer": {{
            "score": 10,
            "comment": "Strongly helps learners understand real-world applications."
        }},
    }}
    "OverallScore": 50,
    "OverallAssessment": "This analogy effectively demonstrates the core concept and is easy to understand with minor improvements possible in explaining differences."
    "Suggestions": "To enhance the analogy, consider ..."
}}
""").strip()

ANALOGY_FILTER_PROMPT = textwrap.dedent("""
You are a filtering and ranking assistance. You will be given {n} analogies in the list of objects with the following JSON format and is required to filter and rank them based on their Overall Score down to {filtered_n} analogies. Output them in the same format as a list of analogies. Here is the JSON format for each analogy:
{{
    "Analogy_Concept": "Filter Bubble",
    "Analogy_Content": "A Filter Bubble is a phenomenon where online platforms use algorithms to personalize content based on a user's behavior and preferences, leading to users only encountering information that aligns with their existing views.",
    "Dimensions": {{
        "StructuralAlignment": {{
            "score": 8,
            "comment": "Captures the main relational elements well, though a few secondary relations are missing."
        }},
        "ProgressiveAlignmentPotential": {{
            "score": 6,
            "comment": "Could be elaborated to highlight more causal sequences."
        }},
        "CommonalitiesAndDifferences": {{
            "score": 8,
            "comment": "Mentions a key mismatch, but could emphasize limitations further."
        }},
        "AbstractionLevelAndLearnerReadiness": {{
            "score": 10,
            "comment": "Perfectly aligns with the intended age group’s background."
        }},
        "ClarityAndEngagement": {{
            "score": 8,
            "comment": "Visually appealing, but would benefit from more explicit role-mapping."
        }},
        "FacilitationOfTransfer": {{
            "score": 10,
            "comment": "Strongly helps learners understand real-world applications."
        }},
    }}
    "OverallScore": 50,
    "OverallAssessment": "This analogy effectively demonstrates the core concept and is easy to understand with minor improvements possible in explaining differences."
    "Suggestions": "To enhance the analogy, consider ..."
}}
""").strip()


ANALOGY_EXTRACTION_PROMPT = textwrap.dedent("""
You are a Language Export that will take an analogical argument that contains a source concept and a target concept, and extract them into a structured format. For example, given the following argument:
"Filter Bubble is like an echo chamber where the algorithmic curation of content acts like the walls of this echo chamber, reflecting your own views and beliefs back to you."
You should extract the source concept "Filter Bubble" and the target concept "Echo Chamber" and provide a structured output in the following format:
{{
    "source": "Filter Bubble",
    "target": "Echo Chamber"
    "argument": "Algorithmic curation of content acts like the walls of this echo chamber, reflecting own views and beliefs back to you."
}}
""").strip()

ANALOGY_PRINCIPLE_PROMPT = textwrap.dedent("""
You are an educational expert who is very capable of analogical approach to teaching. 
You will now teach a group of {audience} about the concept of {concept} using analogies. The concepts is accompanied by a combined knowledge summarization {combined_knowledge}.
You will be provided with the following principles for teaching in an analogical approach:
1. Use well-understood source analogs to capitalize on prior knowledge.
2. Highlight shared causal structure among examples of a structurally defined category using visuospatial, gestural, and verbal supports.
3. Explain correspondences between semantic information and mathematical operations if teaching math. Discuss conceptual meaning of mathematical operations.
4. Use presentation style to facilitate comparison and reduce cognitive load of comparison process when appropriate.
5.Once students have some proficiency with the material, encourage generation of inferences. 

Given the above principles, generate {n} detailed analogy and explanation tailored for such group. You will also generate an appropriate image generation prompt to help the audience better understand the concept.
The output format should in the following format:
{{
    "Analogy": "...",
    "Explanation": "...",
    "Causal Relationship": "...",
    "Image Generation Prompt": "..."
}}
""").strip()

ANALOGY_FILTER_PROMPT_NEW = textwrap.dedent("""
You are an education expert who can filter analogies to see if they fit the current audience group: {audience} based on their current knowledge taxonomy {taxonomy}. 
You will be provided with several analogies in the format of {analogies} and you will do the following:
1. Filter the analogies that are not understandable by the audience.
2. Rank the analogies based on their understandability by te audience.

Return the filtered and ranked analogies in the following format, and make sure the number of analogies is less than or equal to {n}:
{{
    "Analogy": "...",
    "Explanation": "...",
    "Causal Relationship": "...",
    "Image Generation Prompt": "..."
}}
""").strip()

