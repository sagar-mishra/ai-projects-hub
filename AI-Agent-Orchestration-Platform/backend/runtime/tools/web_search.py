import asyncio
from duckduckgo_search import DDGS

def sync_search(query: str) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if not results:
                return "No search results found."
            formatted = []
            for r in results:
                body = r.get('body') or ""
                if len(body) > 500:
                    body = body[:500] + "..."
                formatted.append(f"Title: {r.get('title')}\nLink: {r.get('href')}\nSnippet: {body}\n")
            return "\n---\n".join(formatted)
    except Exception as e:
        return f"Error performing search: {str(e)}"

async def web_search(query: str) -> str:
    """Search the web for a query using DuckDuckGo and return the snippets of top 5 results."""
    return await asyncio.to_thread(sync_search, query)
