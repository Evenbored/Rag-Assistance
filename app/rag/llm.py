import httpx

from app.core.config import settings

class LLMServiceUnavailableError(Exception):
    pass

async def generate_answer(prompt: str) -> str:
    timeout = httpx.Timeout(settings.llm_timeout_seconds)
    
    
    payload ={
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
        },
    }
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{settings.ollama_base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise LLMServiceUnavailableError from exc
    
    data = response.json()
    print(data.get("response", ""))
    return data.get("response", "").strip().replace("""<|channel>thought
<channel|>""", "")