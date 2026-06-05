import httpx
from typing import Optional, Dict, Any

async def http_request(method: str, url: str, headers: Optional[Dict[str, str]] = None, data: Optional[Dict[str, Any]] = None) -> str:
    """Send an HTTP request (GET or POST) to a URL with optional headers and json data, and return the response."""
    method = method.upper()
    if method not in ["GET", "POST"]:
        return "Error: HTTP request tool only supports GET and POST methods."
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            else:
                response = await client.post(url, headers=headers, json=data)
            
            return f"Status Code: {response.status_code}\nResponse Body:\n{response.text}"
    except Exception as e:
        return f"Error sending HTTP request: {str(e)}"
