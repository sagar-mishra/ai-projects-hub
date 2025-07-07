import sys
import os
import streamlit as st
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from indexer import build_faiss_index
from retriever.contextual_reranker import get_compression_retriever
from rag_chain import get_rag_chain 


def is_index_built():
    return os.path.exists("faiss_index/index.faiss") and os.path.exists("faiss_index/index.pkl")


st.title("🔁 FlashRank Compression RAG")

mode = st.selectbox("Choose a mode", ["Search Documents", "Chat with RAG"])

if is_index_built():
    st.success("✅ FAISS index already exists.")
    if st.button("🔄 Rebuild Index Anyway"):
        build_faiss_index()
        st.success("Index rebuilt!")
else:
    if st.button("📦 Build FAISS Index"):
        build_faiss_index()
        st.success("Index built!")


query = st.text_input("Ask your question")

if query and mode == "Search Documents":
    retriever = get_compression_retriever()
    with st.spinner("Running FlashRank reranker..."):
        docs = retriever.invoke(query)

    st.markdown("### 📄 Top Reranked Documents")
    for i, doc in enumerate(docs):
        st.markdown(f"**{i+1}.** {doc.page_content[:300]}...")

elif query and mode == "Chat with RAG":
    rag_chain = get_rag_chain()
    with st.spinner("Asking LLM..."):
        result = rag_chain.invoke(query)

    st.markdown("### 💬 Answer")
    st.write(result["result"])

    st.markdown("### 📄 Reranked Source Docs")
    for i, doc in enumerate(result["source_documents"]):
        st.markdown(f"**{i+1}.** {doc.page_content[:300]}...")