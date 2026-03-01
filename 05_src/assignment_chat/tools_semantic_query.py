import os
from typing import List, Dict, Tuple
from langchain.tools import tool
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from dotenv import load_dotenv
from utils.logger import get_logger

_logs = get_logger(__name__)

load_dotenv()
load_dotenv(".secrets")

CHROMA_DIR = "assignment_chat/chroma_db"
COLLECTION_NAME = "semantic_docs"
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"

API_GATEWAY_KEY = os.getenv("API_GATEWAY_KEY", "")

if not API_GATEWAY_KEY:
    raise RuntimeError("Please set API_GATEWAY_KEY")

client = OpenAI(base_url='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1', 
                api_key='any value',
                default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')})

# ---------------------------------------------------------
# SERVICE 2 — SEMANTIC SEARCH (ChromaDB)
# ---------------------------------------------------------

def get_collection():
    chroma = chromadb.PersistentClient(
        path=CHROMA_DIR,
        settings=Settings(allow_reset=False)
    )
    return chroma.get_collection(COLLECTION_NAME)


def embed(texts: List[str]) -> List[List[float]]:
    resp = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts
    )
    return [d.embedding for d in resp.data]

@tool
def get_semantic_answer(query: str) -> str:
    """
    Returns semantic search responses from knowledgebase.
    """
    col = get_collection()
    q_emb = embed([query])[0]

    results = col.query(
        query_embeddings=[q_emb],
        n_results=3
    )

    docs = results["documents"][0]
    if not docs:
        return "I couldn’t find anything relevant in my local knowledge base."

    context = "\n\n".join(docs)

    prompt = (
        "Use ONLY the context below to answer the question. "
        "If the answer is not in the context, say you don’t know.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}\n\nAnswer:"
    )

    resp = client.responses.create(
        model=CHAT_MODEL,
        input=prompt
    )
    return resp.output[0].content[0].text