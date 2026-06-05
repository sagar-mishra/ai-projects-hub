from backend.runtime.tools.web_search import web_search
from backend.runtime.tools.http_request import http_request
from backend.runtime.tools.calculator import calculator
from backend.runtime.tools.summarizer import summarizer
from langchain_core.tools import StructuredTool
import json

# Tool function map
TOOL_FUNCTIONS = {
    "web_search": web_search,
    "http_request": http_request,
    "calculator": calculator,
    "summarizer": summarizer
}

def load_tools(tools_list_json: str):
    """Given a JSON array of tool names, return a list of LangChain StructuredTool objects."""
    try:
        enabled_names = json.loads(tools_list_json)
    except Exception:
        enabled_names = []

    tools = []
    for name in enabled_names:
        if name in TOOL_FUNCTIONS:
            func = TOOL_FUNCTIONS[name]
            
            # calculator is synchronous, others are async
            is_async = name != "calculator"
            
            tools.append(StructuredTool.from_function(
                coroutine=func if is_async else None,
                func=func if not is_async else None,
                name=name,
                description=func.__doc__ or f"The {name} tool."
            ))
            
    return tools
