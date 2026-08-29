from pathlib import Path
from chronicle.config.loader import *
from chronicle.config.manager import *
from chronicle.storage.schema import init_schema
from chronicle.storage.database import connect
from chronicle.config.credentials import has_api_key,set_api_key
import nltk
import os
import typer

def initialize_chronicle(project_root:Path) -> tuple[Path, bool]:
    chronicle_directory = get_chronicle_directory(project_root)
    chronicle_directory.mkdir(parents=True,exist_ok=True)
    
    db_path = chronicle_directory / "chronicle.db"
    if not db_path.exists():
        db_path.touch()
        
    conn = connect(db_path)
    init_schema(conn)
    
    config_path = get_config_path(project_root)
    created = create_config(config_path)
    
    create_gitignore(project_root)
    
    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        nltk.download("punkt_tab",quiet=True)
    
    return config_path,created

def setup_ai_config(config_path: Path):
    provider = typer.prompt("   AI provider", default="gemini")
    model = typer.prompt("   AI model", default="gemini-2.5-flash")
    if has_api_key(provider):
        typer.echo("   API key already found in the system.")
    else:
        api_key = typer.prompt("   API KEY",hide_input=True)
        set_api_key(provider,api_key)
        typer.echo("   ✓ API key stored securely.")
        
    
    update_ai_config(config_path=config_path,provider=provider,model=model)
