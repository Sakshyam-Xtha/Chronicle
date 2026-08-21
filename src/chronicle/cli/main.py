import typer
from chronicle.cli.commands.init import init
from chronicle.cli.commands.version import version
from chronicle.cli.commands.status import status

app = typer.Typer(
    name="chronicle",
    help="Local-first developer intelligence tool.",
    no_args_is_help=True,
)
  
app.command(name="init")(init)
app.command(name="version")(version)
app.command(name="status")(status)
    
def main():
    app()