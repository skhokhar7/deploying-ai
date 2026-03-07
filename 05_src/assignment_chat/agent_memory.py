'''
How It Works?
1. Short-term memory
    - Keeps the last 5 (default value) messages in RAM for conversational context.
2. Long-term memory
    - Stores facts in agent_memory.json so they persist across sessions.
3. Special commands
    - remember <fact> → Saves a fact to long-term memory.
    - recall [keyword] → Retrieves all facts (or filtered by keyword).
4. Gradio ChatInterface
    - Automatically passes user_message and history to the chatbot function.
    - The bot uses memory to respond with context.
'''
from datetime import datetime
import json
import os

FOLDER_NAME = 'assignment_chat/memory/'
MEMORY_FILE_NAME =  f'{FOLDER_NAME}agent_memory.json'

# ---------------- Memory Manager ----------------
class AgentMemory:
    def __init__(self, memory_file=MEMORY_FILE_NAME, short_term_limit=5):
        self.memory_file = memory_file
        self.short_term_limit = short_term_limit
        self.short_term_memory = []
        self.long_term_memory = self._load_long_term_memory()

    def _load_long_term_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                print("Warning: Memory file corrupted. Starting fresh.")
        return []

    def _save_long_term_memory(self):
        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(self.long_term_memory, f, indent=4)
        except IOError as e:
            print(f"Error saving memory: {e}")

    def remember_short_term(self, role, content):
        self.short_term_memory.append({"role": role, "content": content, "time": datetime.now().isoformat()})
        if len(self.short_term_memory) > self.short_term_limit:
            self.short_term_memory.pop(0)

    def remember_long_term(self, fact):
        self.long_term_memory.append({"fact": fact, "time": datetime.now().isoformat()})
        self._save_long_term_memory()

    def recall_short_term(self):
        return self.short_term_memory

    def recall_long_term(self, keyword=None):
        if keyword:
            return [item for item in self.long_term_memory if keyword.lower() in item["fact"].lower()]
        return self.long_term_memory


def manage_memory(user_message, memory:AgentMemory):
    """
    Memory management logic.
    - Stores conversation in short-term memory
    - Stores facts in long-term memory if user says "remember"
    - Retrieves facts if user says "recall"
    """
    memory.remember_short_term("user", user_message)

    # Simple rule-based memory interaction
    if user_message.lower().startswith("remember"):
        fact = user_message[len("remember"):].strip()
        if fact:
            memory.remember_long_term(fact)
            bot_reply = f"Got it! I will remember: '{fact}'."
        else:
            bot_reply = "Please tell me what to remember."
    elif user_message.lower().startswith("recall"):
        keyword = user_message[len("recall"):].strip()
        facts = memory.recall_long_term(keyword if keyword else None)
        if facts:
            bot_reply = "Here’s what I remember:\n" + "\n".join(f"- {f['fact']}" for f in facts)
        else:
            bot_reply = "I don't remember anything about that."
    else:
        # Example: Echo with short-term context
        context = " | ".join([m["content"] for m in memory.recall_short_term() if m["role"] == "user"])
        bot_reply = f"You said: '{user_message}'. Context so far: {context}"

    memory.remember_short_term("agent", bot_reply)
    return bot_reply