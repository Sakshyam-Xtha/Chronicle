import typer
from chronicle import __version__

def version():
    """Show Chronicle Version"""
    typer.echo(f"Chronicle {__version__}")