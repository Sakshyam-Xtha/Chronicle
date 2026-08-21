from pathlib import Path
from dataclasses import dataclass
from chronicle.project.discovery import find_project_root
from chronicle.config.loader import *

@dataclass
class ProjectStatus:
    project_root:Path
    chronicle_initialized:bool
    git_detected:bool
    config_exists:bool

def get_status() -> ProjectStatus | None:
    project_root = find_project_root()
    if project_root is None:
        return None
    
    config_path = get_config_path(project_root)
    
    return ProjectStatus(
        project_root=project_root,
        chronicle_initialized=config_path.exists(),
        git_detected=(project_root / ".git").exists(),
        config_exists=config_path.exists()
    )