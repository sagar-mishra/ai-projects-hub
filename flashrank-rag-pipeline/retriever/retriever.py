from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.load_local("faiss_index", embedding, allow_dangerous_deserialization=True)

def get_faiss_retriever():

    return db.as_retriever(search_kwargs={"k": 20})
