import httpx
from typing import List, Dict

LLM_SERVER_URL = ""

async def annotate_single_cell(
    client: httpx.AsyncClient, 
    adapter_type: str, 
    message: List[Dict[str, str]]
) -> str:
    """Sends a pre-constructed message array to the custom PEFT LLM server."""
    
    payload = {
        "model": adapter_type,
        "message": message,
        "max_tokens": 50,
        "temperature": 0.0
    }
    
    try:
        response = await client.post(LLM_SERVER_URL, json=payload, timeout=60.0)
        response.raise_for_status()
        return response.json().get("text", "Unknown")
        
    except Exception as e:
        print(f"Inference error: {e}")
        return "Unknown"
