from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv
import tiktoken

load_dotenv()

embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

with open("ScrapeExample.txt", "r") as file:
    text = file.read()

# Get the embedding
embedding = embeddings.embed_query(text)

# Count tokens
encoding = tiktoken.encoding_for_model("text-embedding-3-large")
tokens = encoding.encode(text)
token_count = len(tokens)

print(f"Embedding dimension: {len(embedding)}")
print(f"Token count: {token_count}")