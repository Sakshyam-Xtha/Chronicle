from pathlib import Path
from chronicle.config.loader import *
import tomli_w

DEFAULT_CONFIG = """\
[chronicle]
version=1

[ai]
provider=""
model=""
"""

def create_gitignore(project_root:Path):
    gitignore_path = project_root / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text(".chronicle/\n")
        return
    existing_content = gitignore_path.read_text()
    if ".chronicle/" in existing_content.splitlines():
        return
    with gitignore_path.open(mode="a") as file: 
        file.write("\n.chronicle/\n")

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
    
    