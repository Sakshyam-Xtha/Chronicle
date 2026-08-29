import os 
import keyring

SERVICE_NAME = "chronicle"

def set_api_key(provider:str,api_key:str):
    keyring.set_password(
        SERVICE_NAME,
        provider,
        api_key
    )

def get_api_key(provider: str) -> str | None:
    return keyring.get_password(SERVICE_NAME,provider)

def has_api_key(provider: str) -> bool:
    return get_api_key(provider) is not None