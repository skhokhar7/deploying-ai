from langchain.tools import tool
import time
from utils.logger import get_logger

_logs = get_logger(__name__)

# ---------------------------------------------------------
# SERVICE 3 — FUNCTION CALLING (Calculator + Time)
# ---------------------------------------------------------

@tool
def get_calculate(expression: str) -> str:
    """
    Returns calculation results of the expression.
    """

    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"The result of `{expression}` is {result}"
    except Exception:
        return "I couldn’t evaluate that expression."

@tool
def get_time() -> str:
    """
    Returns current server time.
    """

    return time.strftime("Current server time: %Y-%m-%d %H:%M:%S")