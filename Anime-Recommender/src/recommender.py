from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from src.prompt_template import get_anime_prompt

class AnimeRecommender:

    def __init__(self, retriever, api_key:str, model_name:str):
        self.llm = ChatGroq(
            model=model_name,
            api_key=api_key,
            temperature=0
        )
        self.api_key = api_key

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={
                "prompt": get_anime_prompt()
            }
        )

    def get_recommendation(self, query: str):
        response = self.qa_chain({"query": query})
        return response['result'], response['source_documents']