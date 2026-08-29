from pathlib import Path
try:
    import tomllib #type:ignore
except ModuleNotFoundError:
    import tomli as tomllib

CHRONICLE_DIRECTORY = ".chronicle"
CONFIG_FILE = "config.toml"

def get_chronicle_directory(project_root:Path) -> Path:
    return project_root / CHRONICLE_DIRECTORY

def get_config_path(project_root:Path) -> Path:
    return get_chronicle_directory(project_root=project_root) / CONFIG_FILE

def load_config(config_path: Path) ->dict:
    if not config_path.exists():
        return {}
    
    with config_path.open("rb") as file:
        return tomllib.load(file)