from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from backend.config import settings

def get_llm(model_name: str = None, temperature: float = 0.7, max_tokens: int = 1000):
    """Retrieve LLM client configured based on environment settings and parameters."""
    model = model_name or settings.DEFAULT_MODEL
    
    if settings.GROQ_API_KEY:
        return ChatGroq(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            groq_api_key=settings.GROQ_API_KEY
        )
    else:
        # Fallback to local Ollama. By default Ollama runs OpenAI compatibility API on base_url/v1
        base_url = settings.OLLAMA_BASE_URL or "http://localhost:11434"
        ollama_model = "llama3" if model.startswith("llama3-") else model
        return ChatOpenAI(
            base_url=f"{base_url}/v1",
            api_key="ollama",  # Placeholder
            model=ollama_model,
            temperature=temperature,
            max_tokens=max_tokens
        )
