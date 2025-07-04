import time
import pandas as pd
import os
import sqlite3
from langchain_community.llms import Ollama
from langchain_cache import setup_cache

LOG_FILE = "cache_log.csv"
llm = Ollama(model="mistral")
setup_cache()

def log_cache(prompt, response, latency, cache_status):
    log_entry = {
        "prompt": prompt,
        "response": response,
        "latency_ms": latency,
        "cache_status": cache_status,
        "timestamp": pd.Timestamp.now()
    }
    df = pd.DataFrame([log_entry])
    if not os.path.exists(LOG_FILE):
        df.to_csv(LOG_FILE, index=False)
    else:
        df.to_csv(LOG_FILE, mode='a', header=False, index=False)

def run_prompt(prompt: str):
    start = time.time()
    response = llm.invoke(prompt)
    latency = round((time.time() - start) * 1000, 2)
    cache_status = "HIT" if latency < 100 else "MISS"  # Approx logic
    log_cache(prompt, response, latency, cache_status)
    return response, latency, cache_status

def flush_log_file():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

def flush_cache_db():
    cache_path = ".cache/langchain_cache.db"
    log_file = "cache_log.csv"
    
    if os.path.exists(cache_path):
        try:
            conn = sqlite3.connect(cache_path)
            cursor = conn.cursor()
            tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
            table_names = {t[0] for t in tables}

            if "full_llm_cache" in table_names:
                cursor.execute("DELETE FROM full_llm_cache;")
            elif "langchain_cache" in table_names:
                cursor.execute("DELETE FROM langchain_cache;")

            conn.commit()
            conn.close()
        except Exception as e:
            print("Error while clearing cache:", e)

    # Also remove the logs
    if os.path.exists(log_file):
        os.remove(log_file)