import tiktoken
from networkx.algorithms import isomorphism
from networkx.algorithms import similarity
#import grakel as gk

OPENAI_API_KEY = "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"

def num_tokens_from_string(string, encoding_name):
    encoding = tiktoken.encoding_for_model(encoding_name)
    return len(encoding.encode(string))