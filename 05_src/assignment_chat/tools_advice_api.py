from langchain.tools import tool
import requests
from openai import OpenAI
import os
from dotenv import load_dotenv
from utils.logger import get_logger

_logs = get_logger(__name__)

load_dotenv()
load_dotenv(".secrets")

CHAT_MODEL = "gpt-4o-mini"

API_GATEWAY_KEY = os.getenv("API_GATEWAY_KEY", "")

if not API_GATEWAY_KEY:
    raise RuntimeError("Please set API_GATEWAY_KEY")

client = OpenAI(base_url='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1', 
                api_key='any value',
                default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')})

# ---------------------------------------------------------
# SERVICE 1 — PUBLIC API (Advice API)
# ---------------------------------------------------------

@tool
def get_advice() -> str:
    '''
    Fetches advice from public api.
    '''
    try:
        r = requests.get("https://api.adviceslip.com/advice", timeout=5)
        r.raise_for_status()
        advice = r.json()["slip"]["advice"]

        # Rephrase using OpenAI
        prompt = (
            "Rewrite this advice in a friendly, natural tone, one sentence only:\n"
            f"\"{advice}\""
        )
        resp = client.responses.create(
            model=CHAT_MODEL,
            input=prompt
        )
        _logs.debug(f"Advice: {resp.output[0].content[0].text}")
        return resp.output[0].content[0].text

    except Exception:
        return "The advice service is unavailable right now."