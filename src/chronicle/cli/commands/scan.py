import typer
from chronicle.project.discovery import find_project_root
from chronicle.scanners.git import GitScanner
from chronicle.scanning.engine import ScanEngine

def scan():
    """Scan the project and collect observation"""
    project_root = find_project_root()
    if project_root is None:
        typer.echo("Error: could not find git repo.",err=True)
        raise typer.Exit(code=1)
    
    scanners = [
        GitScanner(project_root),
    ]
    
    engine = ScanEngine(
        project_root=project_root,
        scanners=scanners,
    )
    
    observation = engine.scan()
    typer.echo(f"Collected {len(observation)} observation(s).")