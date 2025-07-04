# 🧠 PromptCache Playground

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup).
* [Directory Structure](#directory-structure)
* [How It Works](#how-it-works)
* [Running the App](#running-the-app)

## General info
<b>🧠 What is Prompt Caching?</b>

Prompt caching is a technique used to store and reuse LLM responses for previously seen prompts, avoiding redundant computation and reducing response latency.

Instead of sending the same prompt repeatedly to the LLM:
<ul>
    <li>The system first checks a cache (in this case, an SQLite database)</li>
    <li>If the prompt was seen before, the cached response is returned instantly</li>
    <li>Otherwise, the LLM is queried, and the new result is stored in the cache for future use</li>
    <li>Otherwise, the LLM is queried, and the new result is stored in the cache for future use</li>
</ul>

This project uses LangChain’s caching system to manage cached responses efficiently with:
<ul>
    <li>SQLiteCache: a lightweight local cache for development/testing</li>
    <li>Cache lookup happens transparently before every prompt execution</li>
    <li>Latency-based detection (< 100ms) is used to infer HIT/MISS in real time</li>
</ul>

✅ Benefits of Prompt Caching<br>
⚡ Speed: Cached responses are returned almost instantly

🧠 Efficiency: Reduces repeated LLM compute calls

💵 Cost-saving: (In API-based setups) prevents redundant billing

🔁 Reproducibility: Same prompt always gives same cached result (unless cleared)

A local, fully offline LangChain + Ollama-powered app to demonstrate prompt caching, visualize cache hits/misses, and benchmark prompt latency — with a real-time UI built using Streamlit.

---

## 🚀 Features

- ⚡ **Prompt Caching via LangChain + SQLite**
- 🧠 **Local LLM via Ollama** (e.g., Mistral, LLaMA3)
- 📊 Real-time **cache HIT/MISS detection**
- 📝 **Prompt logs** (CSV) with latency + timestamps
- 🧹 Flush cache + logs instantly
- 🖥️ Beautiful and minimal **Streamlit UI**
- 🔁 Fully local, **no API keys or internet required**

---

## 📸 Demo

![App Demo](assets/demo/caching1.PNG)
![App Demo](assets/demo/caching2.PNG)
![App Demo](assets/demo/caching3.PNG)
![App Demo](assets/demo/caching4.PNG)

## Technologies
* GenAI
* LangChain
* Ollama
* Streamlit
* SQLite
* Python

## Setup
### Installation 
* Download and install Ollama from https://ollama.com/
* run commands: 
    ollama pull mistral
* pip install -r requirements.txt

## Directory structure
promptcache-playground/

├── app.py                  # Streamlit UI

├── prompt_runner.py        # Core logic (LLM, caching, logging)

├── cache_log.csv           # Prompt logs (auto-created)

├── .cache/                 # LangChain SQLite cache (auto-created)

## 🛠️ How It Works
<b>🔁 Prompt Caching via LangChain</b>
<ul>
    <li>Uses SQLiteCache from LangChain</li>
    <li>When a prompt is run:</li>
    <ul>
        <li>If cached: fetch from SQLite</li>
        <li>If not: LLM is invoked, and response cached</li>
    </ul>
    <li>LLM used: Ollama(model="mistral") (can be changed)</li>
</ul>

<b>🕵️ HIT/MISS Detection</b>
<ul>
    <li>Uses latency threshold (100ms) to infer if cache was hit</li>
    
</ul>

<b>📝 Logging</b>
All prompt runs are logged in cache_log.csv

## ▶️ Running the App
Start your local LLM (e.g., Mistral): 

ollama run mistral

Launch the Streamlit UI:

streamlit run app.py

