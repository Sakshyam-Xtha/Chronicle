from pathlib import Path
from chronicle.project.discovery import find_project_root

def test_find_project_root(tmp_path:Path):
    project = tmp_path / "project"
    project.mkdir()
    
    git_directory = project / ".git"
    git_directory.mkdir()
    
    result = find_project_root(project)
    
    assert result == project

def test_find_project_root_from_nested_directory(tmp_path:Path):
    project = tmp_path / "project"
    project.mkdir()
    
    git_directory = project / ".git"
    git_directory.mkdir()
    
    nested_directory = project/ "src" / "cli" / "projects"
    nested_directory.mkdir(parents=True)
    
    result = find_project_root(nested_directory)
    
    assert result == project

def test_find_project_root_returns_none_when_no_git(tmp_path:Path):
    project = tmp_path / "project"
    project.mkdir()
    
    result = find_project_root(project)
    
    assert result is None