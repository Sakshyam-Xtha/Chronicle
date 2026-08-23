from pathlib import Path
from chronicle.config.loader import *

def initialize_chronicle(project_root:Path) -> tuple[Path, bool]:
    chronicle_directory = get_chronicle_directory(project_root)
    chronicle_directory.mkdir(parents=True,exist_ok=True)
    
    db_path = chronicle_directory / "chronicle.db"
    if not db_path.exists():
        db_path.touch()
    
    config_path = get_config_path(project_root)
    created = False
    
    if not config_path.exists():
        config_path.write_text(
            "[chronicle]\nversion = 1\n"
        )
        created = True
    
    return config_path,created
