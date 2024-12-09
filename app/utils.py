import tiktoken
import openai
import os
#import grakel as gk

MODEL = "gpt-4o"

OPENAI_API_KEY = "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"
client = openai.OpenAI(api_key = OPENAI_API_KEY)


def num_tokens_from_string(string, encoding_name):
    encoding = tiktoken.encoding_for_model(encoding_name)
    return len(encoding.encode(string))

def send_message(model=MODEL, messages=[], n=1):
    content = client.chat.completions.create(model=model, messages=messages, temperature=0.0)
    return content

def parse_message(format, messages=[], model=MODEL):
    content = client.beta.chat.completions.parse(model=model, messages=messages, response_format=format, temperature=0.0)
    return content