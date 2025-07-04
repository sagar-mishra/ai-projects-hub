from fastmcp import Client
from langchain.llms import Ollama
from langchain import LLMChain, PromptTemplate

config = {
    "mcpServers": {
        "math assistant": {"command": "python", "args": ["./mcp_server/mcp_server.py"], "transport": "stdio"},
    }
}

# Connect to local MCP server
client = Client(config)

llm = Ollama(model="mistral")

template = """You are an intelligent math assistant.
You can call tools when appropriate.
{tools}
User: {prompt}
Assistant:"""

prompt = PromptTemplate(input_variables=["tools", "prompt"], template=template)
chain = LLMChain(llm=llm, prompt=prompt)

def ask_math(query: str) -> str:
    tools = client.list_tools()
    resp = chain.run(tools=tools, prompt=query)
    return resp.strip()
