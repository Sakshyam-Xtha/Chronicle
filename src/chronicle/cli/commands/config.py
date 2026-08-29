from pathlib import Path
import typer
from chronicle.project.discovery import find_project_root
from chronicle.config.loader import *
from chronicle.config.manager import *
from chronicle.config.credentials import has_api_key,set_api_key

config_app = typer.Typer(
    help="Manage Chronicle configuration."
)

@config_app.command("set")
def set_config(
    key: str = typer.Argument(...),
    value: str = typer.Argument(...),
):
    """Set a Chronicle config value."""
    project_root = find_project_root()
    if project_root:
        config_path = get_config_path(project_root)
        config = load_config(config_path)
        if key == "provider":   
            update_ai_config(
                config_path,
                provider=value,
            )
        elif key == "model":
            update_ai_config(
                config_path,
                model=value,
            )
        elif key == "api_key":
            if config["ai"]["provider"] != "":
                set_api_key(provider=config["ai"]["provider"],api_key=value)
        else:
            typer.echo(f"Unknown config key: {key}")
            typer.echo("Available key: provider, model, api_key")
            raise typer.Exit(1)
        
        typer.echo(
            f"Updated {key} = {value}"
        )
    else:
        typer.echo("Chronicle not initialized.")
        raise typer.Exit(1)
            
@config_app.callback(invoke_without_command=True)
def config(ctx: typer.Context):
    """View Chronicle configurations."""
    if ctx.invoked_subcommand is not None:
        return
    
    project_root = find_project_root()
    if project_root:
        config_path = get_config_path(project_root)
        configuration = load_config(config_path)
        if not configuration:
            typer.echo("Chronicle config is empty.")
            return
        ai = configuration.get("ai",{})
        
        provider = ai.get("provider","")
        model = ai.get('model', '')
        
        if provider:
            api_status = (
                "configured" if has_api_key(provider) else "not configured"
            )
        else:
            api_status = "not configured"
        
        typer.echo("Chronicle Configuration")
        typer.echo("=======================")
        typer.echo(f"Provider : {provider}")
        typer.echo(f"Model    : {model}")
        typer.echo(f"API Key    : {api_status}")
    else:
        typer.echo("Chronicle not initialized.")
        