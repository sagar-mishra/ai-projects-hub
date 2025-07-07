import os
import shutil
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

def build_faiss_index():
     
    index_path = "faiss_index"

    #remove existing index if it exists
    if os.path.exists(index_path):
        shutil.rmtree(index_path)
        
    loader = TextLoader("data/sample.txt", encoding="utf-8")
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.from_documents(chunks, embedding)
    db.save_local("faiss_index")
    print("Index built and saved to 'faiss_index'.")