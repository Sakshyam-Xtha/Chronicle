import typer
from chronicle.project.discovery import find_project_root
from chronicle.project.initializer import initialize_chronicle,setup_ai_config

def init():
    """Initialize chronicle in a project"""
    
    project_root = find_project_root()
    
    if project_root is None:
        typer.echo(f"Error: No .git files found in the current working directory",err=True)
        raise typer.Exit(code=1)
    
    config_path,created = initialize_chronicle(project_root)
    
    if created:
        typer.echo()
        typer.echo("   ╔══════════════════════════════════════╗")
        typer.echo("   ║          C H R O N I C L E           ║")
        typer.echo("   ╚══════════════════════════════════════╝")
        typer.echo()

        typer.echo("   ✦ Initializing Chronicle...")
        typer.echo()

        typer.echo("   ✓ Project detected")
        typer.echo("   ✓ Chronicle directory created")
        typer.echo("   ✓ Local database initialized")
        typer.echo("   ✓ Initialized NLTK tokenizer")
        typer.echo()
        
        choice = typer.prompt("   Configure AI now?[Y/n] ").lower()
        if choice == "y":
            setup_ai_config(config_path=config_path)
            typer.echo("   ✓ AI successfully configured.")
            typer.echo()
        else:
            typer.echo("   AI not configured.")
            typer.echo("   Use chronicle set command to configure AI.")
            typer.echo()

        typer.echo("   Chronicle is ready.")
        typer.echo()
        typer.echo("   Run `chronicle scan` to begin collecting observations.")
        typer.echo()
    else:
        typer.echo(f"Chronicle already initiated at: {project_root}")