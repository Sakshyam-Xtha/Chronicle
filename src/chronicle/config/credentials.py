import os 

PROVIDER_ENV_VARS = {
    "openai": "OPENAI_API_KEY"
}

def get_api_key(provider: str) -> str | None:
    env_var = PROVIDER_ENV_VARS.get(provider)
    if env_var is None:
        return None
    
    return os.getenv(env_var)

def has_api_key(provider: str) -> bool:
    return get_api_key(provider) is not None