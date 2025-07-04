import subprocess
from client_agent.agent import ask_math
import streamlit as st

# Ensure MCP math server is running
subprocess.Popen(["python", "../mcp_server/math_server.py"])

st.title("🔢 Math-MCP POC")

query = st.text_input("Ask a math question, e.g., 'What is 12 times 7?'")

if st.button("Calculate") and query:
    with st.spinner("Thinking..."):
        answer = ask_math(query)
    st.write("**Answer:**", answer)
