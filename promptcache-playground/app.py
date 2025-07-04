import streamlit as st
from prompt_runner import run_prompt, flush_log_file, flush_cache_db, LOG_FILE
import pandas as pd
import os

st.set_page_config(page_title="PromptCache Playground", layout="wide")
st.title("🧠 PromptCache Playground")

prompt = st.text_area("Enter your prompt:", height=150)

if st.button("Run with LangChain") and prompt.strip():
    response, latency, status = run_prompt(prompt)
    st.success(f"Response (Cache: {status}, Time: {latency}ms)")
    st.code(response)

st.markdown("---")
st.header("📊 Cache Logs")

if os.path.exists(LOG_FILE):
    df = pd.read_csv(LOG_FILE)
    st.dataframe(df.tail(20), use_container_width=True)

    if st.button("Flush Logs"):
        flush_log_file()
        st.success("Logs flushed!")
        st.rerun()

if st.button("Flush Cache DB"):
    flush_cache_db()
    st.success("Cache reset!")
    st.rerun()
