from chronicle.ai.base import AIProvider
from chronicle.ai.openai import OpenAIProvider
from chronicle.ai.google_ai import GenAIProvider

def create_provider(
    provider: str,
    model:str,
    api_key:str
) -> AIProvider:
    if provider == "openai":
        return OpenAIProvider(
            api_key=api_key,
            model=model,
        )
    elif provider == "gemini":
        return GenAIProvider(
            api_key=api_key,
            model=model,
        )
        
    raise ValueError(
        f"Unsupported AI provider: {provider}"
    )