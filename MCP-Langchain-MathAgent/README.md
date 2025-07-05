# 🔢 MCP-Langchain-MathAgent

An interactive AI-powered math assistant that uses **LangChain**, **Ollama**, and the **FastMCP** framework to dynamically reason about and call mathematical tools like `add`, `subtract`, and `divide` — all running **locally**. This project showcases how LLMs can use structured tools via **Model Context Protocol (MCP)** with zero external API dependencies.

---

## 🚀 What is MCP?

**Model Context Protocol (MCP)** is an open protocol that defines how tools (APIs, functions, etc.) are exposed to large language models in a structured way.

**FastMCP** is a lightweight Python framework for building MCP-compatible tool servers easily.

🔗 Official GitHub: [https://github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)  
🌐 Website: [https://gofastmcp.com](https://gofastmcp.com)

---

## 📌 Project Overview

| Feature                     | Description                                             |
|---------------------------- |---------------------------------------------------------|
| 🧠 LLM                      | Mistral 7B via [Ollama](https://ollama.com/)            |
| 🔗 Agent Framework          | [LangChain](https://www.langchain.com/)                 |
| 🛠️ Tool Interface           | [FastMCP](https://github.com/jlowin/fastmcp)            |
| 🌐 UI                       | [Streamlit](https://streamlit.io/) Web Interface        |
| 🔒 Privacy                  | 100% local — no cloud or API keys required              |

---

## 🧠 How It Works

This project shows how an LLM can reason about a question, discover tools dynamically, and call the correct one using **MCP**:

1. ✅ The MCP server exposes math tools (`add`, `multiply`, etc.)
2. ✅ The LangChain agent fetches available tools via `MCPClient`
3. ✅ The LLM (Mistral via Ollama) receives the tools + user prompt
4. ✅ LLM chooses the right tool and returns the answer
5. ✅ The answer is shown in the Streamlit UI

---

## 📁 Folder Structure
MCP-Langchain-MathAgent/ <br>
├── app.py # Streamlit UI <br>
├── requirements.txt # Python dependencies <br>
│   <br>
├── client_agent/ <br>
│ ├── init.py <br>
│ └── agent.py # LangChain agent with MCP client <br>
│   <br>
└── mcp_server/ <br>
├── init.py <br>
└── mcp_server.py # FastMCP server with math tools <br>

--- 

## Set Up Python Environment
conda create -n langchain_env python=3.10 -y <br>
conda activate langchain_env <br>
pip install -r requirements.txt <br>

<b>Install Ollama and Pull Model</b> <br>
Install Ollama: https://ollama.com/download <br>
Then pull Mistral: <br>
ollama pull mistral

## ▶️ Run the App
streamlit run app.py

This will:
<ul> 
    <li>🔄 Start the MCP server in the background</li>
    <li>⚙️ Launch the Streamlit UI</li>
    <li>🧠 Accept math queries like: What is 25 divided by 5?</li>
</ul>

🔄 Start the MCP server in the background

⚙️ Launch the Streamlit UI

🧠 Accept math queries like:
What is 25 divided by 5?

## 🔍 Behind the Scenes (Workflow) 
<ol> 
<li> UI Input: User enters: "What is 25 divided by 5?" </li>
<li> Agent Fetches Tools: client.get_tools_summary() → [add(), subtract(), divide(), ...] </li>
<li> LangChain Prompting: <br>
You are an intelligent math assistant.<br>
You can call tools when appropriate.<br>
Tools: add(a, b), subtract(a, b), ...<br>
User: What is 25 divided by 5?<br>
Assistant:<br></li>
<li>LLM Response: divide(25, 5) → 5</li>
<li>Output: Streamlit shows result</li>
</ol>


