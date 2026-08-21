import typer
from chronicle.cli.commands.init import init
from chronicle.cli.commands.version import version

app = typer.Typer(
    name="chronicle",
    help="Local-first developer intelligence tool.",
)
  
app.command(name="init")(init)
app.command(name="version")(version)
    
def main():
    app()