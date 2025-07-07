from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import FlashrankRerank
from retriever.retriever import get_faiss_retriever

def get_compression_retriever():
    base_retriever = get_faiss_retriever()
    compressor = FlashrankRerank()  # Uses default ms-marco MiniLM reranker
    return ContextualCompressionRetriever(
        base_retriever=base_retriever,
        base_compressor=compressor
    )
