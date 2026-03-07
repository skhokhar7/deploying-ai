'''
Offline Embedding Script
Run this only once to populate ChromaDB.
Keep dataset tiny (<40 MB)
'''

import json
import chromadb
from chromadb.config import Settings
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv('.secrets')

if not os.getenv("API_GATEWAY_KEY"):
    raise RuntimeError("API_GATEWAY_KEY not found. Check .secrets or your env.")

# client = OpenAI()
client = OpenAI(base_url='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1', 
                api_key='any value',
                default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')})

# Variable definition
EMBED_MODEL = "text-embedding-3-small"
CHROMA_DIR = "assignment_chat/chroma_db"
COLLECTION_NAME = "semantic_docs"

# Load your dataset
with open("assignment_chat/data/semantic_docs.json") as f:
    docs = json.load(f)

texts = [d["text"] for d in docs]
ids = [d["id"] for d in docs]

# Create embeddings
resp = client.embeddings.create(
    model=EMBED_MODEL,
    input=texts
)
embs = [d.embedding for d in resp.data]

# Store in Chroma
chroma = chromadb.PersistentClient(
    path=CHROMA_DIR,
    settings=Settings(allow_reset=True)
)
chroma.reset()

col = chroma.create_collection(COLLECTION_NAME)
col.add(
    documents=texts,
    embeddings=embs,
    ids=ids
)

print("ChromaDB populated.")