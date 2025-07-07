# 🔍 FlashRank RAG: Document Search + QA with LangChain, FAISS & FlashRank

A minimal, production-ready RAG (Retrieval-Augmented Generation) app that supports both:

- 📄 Document Search with Reranking (FlashRank)
- 💬 LLM-based Q&A from reranked document context
---

## 🔁 What is Reranking and Why It Matters?

In traditional RAG pipelines, the retriever (e.g., FAISS) fetches documents based purely on vector similarity — which may not always reflect the **most relevant context** for answering the question.

Reranking solves this by:

1. 🔎 Fetching **top-k** documents via semantic search (FAISS)
2. ⚡ Passing them through a **reranker model** (like FlashRank)
3. 📊 Sorting them based on how well they answer the query — not just similarity

This ensures your LLM gets the **most question-relevant chunks**, not just the most similar ones.

### 🧠 FlashRank in This Project

This app uses **LangChain's `FlashrankRerank`** via `ContextualCompressionRetriever` to perform fast and accurate reranking before the answer is generated.
--

## 🚀 Features

| Feature                        | Description                                                                 |
|--------------------------------|-----------------------------------------------------------------------------|
| ✅ Search Mode                 | Displays reranked documents only                                           |
| ✅ Chat Mode                   | Uses LLM to answer questions from top-ranked docs                         |
| ✅ FAISS Vector Store          | Efficient semantic indexing of your documents                             |
| ⚡ FlashRank Reranker          | Improves answer/document relevance using reranking                        |
| 🔄 Dynamic Index Rebuilding    | Rebuild FAISS index from `sample.txt` anytime                             |
| 🛠️ Fully Local Setup           | Works with Ollama models (e.g. `mistral`, `llama3`)                        |

---

## 🗂️ Project Structure

flashrank-rag-pipeline/
├── app.py # Streamlit UI
├── indexer.py # Builds & clears FAISS index
├── rag_chain.py # RAG chain wrapper
├── requirements.txt # Python dependencies
├── data/
│ └── sample.txt # Your input document
└── retriever/
  └── retriever.txt # FAISS retriever
  └── contextual_reranker.py # FlashRank + compression retriever


--

## 🧠 Usage

<b> 1. 📝 Add Your Data </b> <br>
Replace the contents of: data/sample.txt <br>
with your own .txt data or parsed output (e.g., from PDFs).
<br>

<b> 2. 🚀 Run the App </b> <br>
streamlit run app.py 
<br>

<b> 3. 📌 Modes in UI </b> <br>
<ul>
    <li>Search Documents → See reranked source documents</li>
    <li>Chat with RAG → Ask questions and get answers from LLM + top docs</li>
</ul>

<b> 4. 🔄 Rebuild the Index </b> <br>
If you've updated sample.txt, click: 🔄 Rebuild Index Anyway <br>
This deletes the old FAISS index and builds a fresh one.



