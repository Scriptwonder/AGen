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