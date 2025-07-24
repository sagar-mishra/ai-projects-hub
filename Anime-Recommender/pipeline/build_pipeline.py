from src.data_loader import AnimeDataLoader
from src.vector_store import VectorStoreBuilder
from utils.logger import get_logger
from utils.custom_exception import CustomException
from dotenv import load_dotenv

load_dotenv()

logger = get_logger(__name__)

def main():
    try:
        logger.info("Starting Anime Recommender Pipeline...")
        loader = AnimeDataLoader("data/anime_with_synopsis.csv", "data/anime_with_synopsis.csv")
        processed_csv = loader.load_and_process()

        logger.info("Data loaded and processed successfully.")

        vector_builder = VectorStoreBuilder(csv_path=processed_csv, persist_dir="chroma_db")
        vector_builder.build_and_save_vector_store()
        logger.info("Vector store built and saved successfully.")
        logger.info("Pipeline built successfully.")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise CustomException("An error occurred in the pipeline") from e
    
if __name__ == "__main__":
    main()