import faiss
import numpy as np
import os
from typing import List
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client (v1.x)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define your embedding model
EMBEDDING_MODEL = "text-embedding-ada-002"

# Embed list of text chunks
def embed_text(texts: List[str]) -> List[List[float]]:
    res = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )
    return [r.embedding for r in res.data]

# Build FAISS index from chunk embeddings
def build_faiss_index(chunks: List[str]):
    vectors = embed_text(chunks)
    dim = len(vectors[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(vectors).astype("float32"))
    return index, vectors

# Perform semantic search using FAISS
def search_index(index, query: str, chunks: List[str], top_k=5):
    query_embedding = embed_text([query])[0]
    D, I = index.search(np.array([query_embedding]).astype("float32"), top_k)
    return [chunks[i] for i in I[0]]
