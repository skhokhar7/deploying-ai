from langchain.tools import tool
import os
import requests
from dotenv import load_dotenv
from utils.logger import get_logger

_logs = get_logger(__name__)

load_dotenv()
load_dotenv(".secrets")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

if not TAVILY_API_KEY:
    raise RuntimeError("Please set TAVILY_API_KEY")

@tool
def search_web(query):
    '''
    Fetches web search results.
    '''
    if not TAVILY_API_KEY:
        return "Web search is not configured. Please set TAVILY_API_KEY."
    try:
        url = "https://api.tavily.com/search"
        payload = {"api_key": TAVILY_API_KEY, "query": query, "max_results": 3}
        r = requests.post(url, json=payload, timeout=8)
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results:
            return "No search results found."
        formatted = "\n".join([f"- {res['title']}: {res['url']}" for res in results])
        _logs.debug(f"Here are some search results for '{query}':\n{formatted}")
        return f"Here are some search results for '{query}':\n{formatted}"
    except Exception as e:
        return f"Error performing web search: {e}"
