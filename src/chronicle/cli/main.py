import typer
from chronicle.cli.commands.init import init
from chronicle.cli.commands.version import version
from chronicle.cli.commands.status import status
from chronicle.cli.commands.scan import scan
from chronicle.cli.commands.show import show
from chronicle.cli.commands.analyze import analyze

app = typer.Typer(
    name="chronicle",
    help="Local-first developer intelligence tool.",
    no_args_is_help=True,
)
  
app.command(name="init")(init)
app.command(name="version")(version)
app.command(name="status")(status)
app.command(name="scan")(scan)
app.command(name="show")(show)
app.command(name="analyze")(analyze)
    
def main():
    app()