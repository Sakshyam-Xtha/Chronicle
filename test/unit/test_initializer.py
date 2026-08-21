from pathlib import Path
from chronicle.project.initializer import *

def test_chronicle_init_creates_chronicle_directory(tmp_path:Path):
    project = tmp_path / "project"
    project.mkdir()
    
    config_path,created = initialize_chronicle(project)
    
    assert created is True 
    assert config_path.exists()
    assert config_path.parent.name == ".chronicle"
    
def test_chronicle_init_creates_valid_config(tmp_path:Path):
    project = tmp_path / "project"
    project.mkdir()
        
    config_path, _ = initialize_chronicle(project)
    
    content = config_path.read_text(encoding="utf-8")
    
    assert "[chronicle]" in content
    assert "version = 1" in content

def test_chronicle_init_does_not_overwrite_existing_config(tmp_path:Path):
    project = tmp_path / "project"
    project.mkdir()
        
    config_path, first_created = initialize_chronicle(project)
    config_path,second_created = initialize_chronicle(project)
    
    assert first_created is True
    assert second_created is False