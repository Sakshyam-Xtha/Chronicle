import typer
from chronicle.project.discovery import find_project_root
from chronicle.scanning.scanners.git import GitScanner
from chronicle.scanning.scanners.django_migrations import DjangoMigrationScanner
from chronicle.scanning.engine import ScanEngine
from chronicle.config.loader import get_chronicle_directory
from chronicle.storage.database import connect
from chronicle.storage.observations import ObservationRepo
from chronicle.storage.scan_state import ScanStateRepo
from chronicle.scanning.context import ScanContext

def scan():
    """Scan the project and collect observation"""
    project_root = find_project_root()
    if project_root is None:
        typer.echo("Error: could not find git repo.",err=True)
        raise typer.Exit(code=1)
    
    db_path = (get_chronicle_directory(project_root) / "chronicle.db")
    connection = connect(database_path=db_path)
    scan_state = ScanStateRepo(connection)
    repo = ObservationRepo(connection)
    last_commit = scan_state.get(
        "last_commit",
        "git",
    )
    context = ScanContext(
        state={
            "git.last_commit":last_commit,
        }
    )
    
    scanners = [
        GitScanner(project_root),
        DjangoMigrationScanner(project_root)
    ]
    
    engine = ScanEngine(
        project_root=project_root,
        scanners=scanners, #type: ignore
    )
    
    observations = engine.scan(context=context)
    
    created_count = 0
    
    with connection:
        for observation in observations:
            if repo.save(observation=observation):
                created_count+=1
    
        if observations:
            newest_commit = observations[0].external_id
            scan_state.set(
                "last_commit",
                "git",
                newest_commit
            )
        
    connection.close()
    
    if created_count > 0:
        typer.echo(f"Collected {len(observations)} observation(s).")
        typer.echo(f"Stored {created_count} new observation(s)")
    else:
        typer.echo(f"Collected {len(observations)} observation(s).")
        typer.echo(f"All observation(s) already stored.")