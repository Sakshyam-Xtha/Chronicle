import typer
from chronicle.project.discovery import find_project_root

def init():
    """Initialize chronicle in a project"""
    project_root = find_project_root()
    if project_root is not None:
        typer.echo(f"Initializing Chronicle at: {project_root}")
    else:
        typer.echo(f"Error: No .git files found in the current working directory",err=True)
        raise typer.Exit(code=1)