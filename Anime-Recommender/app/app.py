import streamlit as st
from pipeline.pipeline import AnimeRecommenderPipeline
from dotenv import load_dotenv

st.set_page_config(page_title="Anime Recommender", layout="wide")

load_dotenv()

@st.cache_resource
def init_pipeline():
    try:
        pipeline = AnimeRecommenderPipeline(persist_dir="chroma_db")
        return pipeline
    except Exception as e:
        st.error(f"Failed to initialize the recommender pipeline: {str(e)}")
        return None
    
pipeline = init_pipeline()

st.title("Anime Recommender System")

query = st.text_input("Enter your anime preferences eg. : Naruto")

if query:
    with st.spinner("Fetching recommendations..."):
        response = pipeline.recommend(query)
        st.markdown("### Recommendations:")
        st.write(response)
