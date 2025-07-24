from src.vector_store import VectorStoreBuilder
from src.recommender import AnimeRecommender
from config.config import GROQ_API_KEY, MODEL_NAME
from utils.logger import get_logger
from utils.custom_exception import CustomException

logger = get_logger(__name__)

class AnimeRecommenderPipeline:
    def __init__(self,persist_dir:str="chroma_db"):
        try:
            logger.info("Initializing Anime Recommender Pipeline...")
            vector_builder = VectorStoreBuilder(csv_path="", persist_dir=persist_dir)
            retriever = vector_builder.load_vector_store().as_retriever()
            self.recommender = AnimeRecommender(
                retriever=retriever,
                api_key=GROQ_API_KEY,
                model_name=MODEL_NAME
            )
        except Exception as e:
            logger.error(f"An error occurred while initializing the pipeline: {str(e)}")
            raise CustomException("Failed to initialize Anime Recommender Pipeline") from e
    
    def recommend(self, query: str):
        try:
            logger.info(f"Received a query {query}")
            recommendation, source_documents = self.recommender.get_recommendation(query)
            logger.info("Recommendation retrieved successfully.")
            return recommendation
        except Exception as e:
            logger.error(f"An error occurred while getting recommendation: {str(e)}")
            raise CustomException("Failed to get recommendation") from e