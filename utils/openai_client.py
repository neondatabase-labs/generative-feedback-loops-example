from openai import AzureOpenAI
from utils.config import OPENAI_ENDPOINT, OPENAI_API_KEY, EMBEDDING_MODEL, GPT_MODEL


openai_client = AzureOpenAI(
    azure_endpoint=OPENAI_ENDPOINT,
    api_key=OPENAI_API_KEY,
    api_version="2024-02-01",
)


def generate_embeddings(text):
    response = openai_client.embeddings.create(input=text, model=EMBEDDING_MODEL)
    embeddings = response.data[0].embedding
    return embeddings


def generate_summary(prompt):
    response = openai_client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content
