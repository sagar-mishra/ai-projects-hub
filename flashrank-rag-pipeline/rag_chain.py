from langchain.chains import RetrievalQA
from langchain.llms import Ollama
from retriever.contextual_reranker import get_compression_retriever

retriever = get_compression_retriever()
llm = Ollama(model="mistral")


def get_rag_chain():

    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
