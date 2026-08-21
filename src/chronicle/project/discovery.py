from pathlib import Path

def find_project_root(start:Path | None=None) -> Path | None:
    """Find the nearest ancestor containing a .git directory"""
    cwd = start or Path.cwd()
    for directory in [cwd,*cwd.parents]:
        if (directory / ".git").exists():
            return directory
    return None