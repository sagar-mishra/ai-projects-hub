import os
from langchain.globals import set_llm_cache
from langchain.cache import SQLiteCache

def setup_cache():
    os.makedirs(".cache", exist_ok=True)
    set_llm_cache(SQLiteCache(database_path=".cache/langchain_cache.db"))


