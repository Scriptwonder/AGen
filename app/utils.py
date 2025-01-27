import tiktoken
import openai
import os
#import grakel as gk

MODEL = "gpt-4o"

OPENAI_API_KEY = "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"
client = openai.OpenAI(api_key = OPENAI_API_KEY)
groups = ["Pre-School Kids", "Middle Schooler", "College Undergraduate"]
habits = ["Comic Books", "Animals", "Sports"]


def num_tokens_from_string(string, encoding_name):
    encoding = tiktoken.encoding_for_model(encoding_name)
    return len(encoding.encode(string))

def send_message(model=MODEL, messages=[], n=1):
    content = client.chat.completions.create(model=model, messages=messages, temperature=0.0, max_completion_tokens=16384)
    return content

def parse_message(format, messages=[], model=MODEL, n=1):
    content = client.beta.chat.completions.parse(model=model, messages=messages, response_format=format, temperature=0.0, n=n, max_completion_tokens=16384)
    return content

def generate_image(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )
    return response.data[0].url

if __name__ == "__main__":
    import numpy as np
    import seaborn as sns
    import matplotlib.pyplot as plt

    # -----------------------------
    # 1) Confusion Matrix by AUDIENCE LEVEL
    # -----------------------------
    # From the calculations we have:
    #    Actual \ Pred     College U.   Middle Schooler   Pre-School
    #  -------------------------------------------------------------
    #    College U.           5              4              6
    #    Middle Schooler      3              5              7
    #    Pre-School           0              3             12

    cm_audience = np.array([
        [5,  4,  6],
        [3,  5,  7],
        [0,  3, 12]
    ])

    audience_labels = ['College U.', 'Middle Schooler', 'Pre-School']

    plt.figure(figsize=(5,4))
    sns.heatmap(cm_audience, annot=True, fmt='d',
                xticklabels=audience_labels, yticklabels=audience_labels,
                cmap='Blues')
    plt.title("Confusion Matrix by Audience Level")
    plt.xlabel("Predicted Audience")
    plt.ylabel("Actual Audience")
    plt.show()


    # -----------------------------
    # 2) Confusion Matrix by INTEREST
    # -----------------------------
    # From the calculations we have:
    #    Actual \ Pred     Animals   Comic Books   Sports
    #  ----------------------------------------------
    #    Animals             11          2           2
    #    Comic Books          0         14           1
    #    Sports               1          0          14

    cm_interest = np.array([
        [11,  2,  2],
        [ 0, 14,  1],
        [ 1,  0, 14]
    ])

    interest_labels = ['Animals', 'Comic Books', 'Sports']

    plt.figure(figsize=(5,4))
    sns.heatmap(cm_interest, annot=True, fmt='d',
                xticklabels=interest_labels, yticklabels=interest_labels,
                cmap='Greens')
    plt.title("Confusion Matrix by Interest")
    plt.xlabel("Predicted Interest")
    plt.ylabel("Actual Interest")
    plt.show()

