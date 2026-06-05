from backend.runtime.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate

async def summarizer(text: str) -> str:
    """Summarize a large block of text into a concise and clear summary using the configured LLM."""
    if not text or not text.strip():
        return "No text provided to summarize."
        
    try:
        # Standard configuration for summary: lower temperature for more determinism
        llm = get_llm(temperature=0.3, max_tokens=1000)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a professional summarizer. Provide a clear, structured, and concise summary of the text. Focus on the core information and key takeaways."),
            ("user", "Please summarize the following text:\n\n{text}")
        ])
        
        chain = prompt | llm
        response = await chain.ainvoke({"text": text})
        return response.content
    except Exception as e:
        return f"Error performing summarization: {str(e)}"
