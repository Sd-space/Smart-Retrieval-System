# test_openai_embedding.py
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

res = client.embeddings.create(
    model="text-embedding-ada-002",
    input=["Hello, world!"]
)

print(res.data[0].embedding[:5])  # show first 5 dimensions
