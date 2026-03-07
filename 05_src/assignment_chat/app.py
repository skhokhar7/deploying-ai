from assignment_chat.main import get_graph
from langchain_core.messages import HumanMessage, AIMessage
import gradio as gr
from assignment_chat.agent_memory import AgentMemory
from assignment_chat.agent_memory import manage_memory
from utils.logger import get_logger

_logs = get_logger(__name__)

llm = get_graph()

# ---------------------------------------------------------
# Short and Long-term Memory Management
# ---------------------------------------------------------

MAX_TURNS = 16  # short-term memory window
memory = AgentMemory(short_term_limit=MAX_TURNS)

# ---------------------------------------------------------
# GUARDRAILS
# ---------------------------------------------------------

RESTRICTED = [
    "cat", "cats",
    "dog", "dogs",
    "horoscope", "horoscopes",
    "zodiac", "zodiac sign", "zodiac signs",
    "taylor swift"
]

PROMPT_ACCESS = [
    "system prompt",
    "your system prompt",
    "show me your prompt",
    "reveal your prompt",
    "change your system prompt",
    "modify your system prompt",
]

def guardrails(user_text: str) -> str:
    t = user_text.lower()

    if any(k in t for k in RESTRICTED):
        return "I can’t talk about that topic. Try something else."

    if any(k in t for k in PROMPT_ACCESS):
        return "I can’t reveal or modify my system prompt, but I’m happy to help with anything else."

    return ""

# ---------------------------------------------------------
# Chatbot Function
# ---------------------------------------------------------

def chatbot_fn(message: str, history: list[dict]) -> str:
    # Guardrails first
    g = guardrails(message)
    if g:
        return g
    
    langchain_messages = []
    n = 0
    _logs.debug(f"History: {history}")
    for msg in history:
        if msg['role'] == 'user':
            langchain_messages.append(HumanMessage(content=msg['content']))
        elif msg['role'] == 'assistant':
            langchain_messages.append(AIMessage(content=msg['content']))
            n += 1
    langchain_messages.append(HumanMessage(content=manage_memory(message, memory)))
    langchain_messages.append(HumanMessage(content=message))

    state = {
        "messages": langchain_messages,
        "llm_calls": n
    }

    response = llm.invoke(state)
    return response['messages'][len(response['messages']) - 1].content

# ---------------------------------------------------------
# Chatbot UI
# ---------------------------------------------------------

chat = gr.ChatInterface(
    title="Agentic AI Chatbot",
    description="This chatbot remembers short-term conversation and can store/retrieve long-term facts.\n"
                "Commands:\n"
                "- `remember <fact>` → Store in long-term memory\n"
                "- `recall [keyword]` → Retrieve from long-term memory",
    fn=chatbot_fn,
    type="messages",
    chatbot=gr.Chatbot(height=500,
                       avatar_images=["assignment_chat/images/user.jpg", "assignment_chat/images/mentor.jpg"],
                       show_copy_button=True,
                       show_copy_all_button=True,
                       ),
    theme="soft",
)

# ---------------------------------------------------------
# Main Function Launch
# ---------------------------------------------------------

if __name__ == "__main__":
    _logs.info('Starting Chatbot App...')
    chat.launch()
