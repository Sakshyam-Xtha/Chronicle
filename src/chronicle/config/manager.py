from pathlib import Path
try:
    import tomllib #type:ignore
except ModuleNotFoundError:
    import tomli as tomllib
import tomli_w
    
from chronicle.config.loader import *

DEFAULT_CONFIG = """\
[chronicle]
version=1

[ai]
provider=""
model=""
"""

def create_config(config_path:Path) -> bool:
    if not config_path.exists():
        config_path.write_text(
            DEFAULT_CONFIG
        )
        return True
    return False

def update_ai_config(
    config_path:Path,
    provider:str | None = None,
    model:str | None=None,
) -> None:
    if not config_path.exists():
        create_config(config_path)
    
    config = load_config(config_path)
    
    ai = config.setdefault("ai",{})
    if provider is not None:
        ai["provider"] = provider
    if model is not None:
        ai["model"] = model
    
    with config_path.open("wb") as file:
        tomli_w.dump(config,file)
    
    