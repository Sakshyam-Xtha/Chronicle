import typer
from chronicle.project.discovery import find_project_root
from chronicle.config.loader import get_chronicle_directory, load_config, get_config_path
from chronicle.interpretation.context_builder import *
from chronicle.storage.database import connect
from chronicle.storage.findings import FindingsRepo
from chronicle.storage.observations import ObservationRepo
from chronicle.interpretation.interpreter import Interpreter
from chronicle.ai.factory import GenAIProvider
from chronicle.config.credentials import get_api_key

def interpret(query: str = typer.Option(...,"--question","-q",help="Question to ask the project history.")):
    """Interpret Chronicle's project history using AI."""
    project_root = find_project_root()
    if project_root is None:
        typer.echo("Chronicle project not found.")
        raise typer.Exit(1)
    
    db_path = (get_chronicle_directory(project_root) / "chronicle.db")
    
    conn = connect(db_path)
    
    findings_repo = FindingsRepo(conn)
    observation_repo = ObservationRepo(conn)
    
    findings = findings_repo.list_all()
    observations = observation_repo.list_all()
    
    context = build_context(
        question=query,
        findings=findings,
        observations=observations)
    
    config_path = get_config_path(project_root)
    config = load_config(config_path)
    ai = config.get("ai",{})
    model = ai.get("model")
    provider_name = ai.get("provider")
    api_key = get_api_key(provider=provider_name)
    if not api_key:
        typer.echo(f"Couldn't find an api key for {provider_name} provider")
        raise typer.Exit(1)
    provider = GenAIProvider(model=model,api_key=api_key)
    
    interpreter = Interpreter(provider=provider)
    response = interpreter.interpret(context)
    
    typer.echo(response)