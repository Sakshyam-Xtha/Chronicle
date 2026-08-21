from pathlib import Path
from chronicle.config.loader import *

def initialize_chronicle(project_root:Path) -> Path:
    chronicle_directory = get_chronicle_directory(project_root)
    chronicle_directory.mkdir(parents=True,exist_ok=True)
    
    config_path = get_config_path(project_root)
    config_path.write_text(
        "[chronicle]\nversion = 1\n"
    )
    
    return config_path
