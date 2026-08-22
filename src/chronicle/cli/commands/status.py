from pathlib import Path
from chronicle.project.status import get_status
import typer

def status():
    """Show the current chronicle project status."""
    project_status=get_status()
    if project_status is None:
        typer.echo("Error: could not find a Git repo in the project.")
        raise typer.Exit(code=1)
    
    typer.echo("")    
    typer.echo(f"Project: {project_status.project_root.name}")    
    typer.echo(f"Root: {project_status.project_root}")    
    if project_status.chronicle_initialized:
        typer.echo("Chronicle: initialized")
    else:
        typer.echo("Chronicle: not initialized")
    if project_status.git_detected:
        typer.echo("Git: detected")
    else:
        typer.echo("Git: not detected")
    if project_status.config_exists:
        typer.echo("Configuration: found")
    else:
        typer.echo("Configuration: missing")
