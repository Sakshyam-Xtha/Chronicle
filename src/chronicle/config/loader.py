from pathlib import Path

CHRONICLE_DIRECTORY = ".chronicle"
CONFIG_FILE = "config.toml"

def get_chronicle_directory(project_root:Path) -> Path:
    return project_root / CHRONICLE_DIRECTORY

def get_config_path(project_root:Path) -> Path:
    return get_chronicle_directory(project_root=project_root) / CONFIG_FILE