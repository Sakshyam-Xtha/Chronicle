import typer
from chronicle.project.discovery import find_project_root
from chronicle.project.initializer import initialize_chronicle

def init():
    """Initialize chronicle in a project"""
    
    project_root = find_project_root()
    
    if project_root is None:
        typer.echo(f"Error: No .git files found in the current working directory",err=True)
        raise typer.Exit(code=1)
    
    config_path = initialize_chronicle(project_root)
    
    typer.echo(f"Chronicle initiated at: {project_root}")
    typer.echo(f"Configuration at: {config_path}")