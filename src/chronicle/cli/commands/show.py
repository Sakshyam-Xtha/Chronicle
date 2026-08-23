import typer
from chronicle.storage.observations import ObservationRepo
from chronicle.storage.database import connect
from chronicle.config.loader import get_chronicle_directory
from chronicle.project.discovery import find_project_root

def show(id:int | None = typer.Option(None, "--id")):
    project_root = find_project_root()
    if project_root is None:
            typer.echo("Error: could not find git repo.",err=True)
            raise typer.Exit(code=1)
    db_path = (get_chronicle_directory(project_root) / "chronicle.db")
    conn = connect(db_path)
    if id:
        """Shows observation by id."""
        observation, = ObservationRepo(conn).list_all(id)
        typer.echo()
        typer.echo(f"Observation #{id}")
        typer.echo("─" * 44)
        typer.echo()

        typer.echo(f"{'Source:':<14}{observation.source}")
        typer.echo(f"{'Type:':<14}{observation.type}")
        typer.echo(f"{'External ID:':<14}{observation.external_id}")
        typer.echo(
            f"{'Timestamp:':<14}"
            f"{observation.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )

        typer.echo()
        typer.echo("Data")
        typer.echo("─" * 44)

        data = observation.data

        if "app" in data:
            typer.echo(f"{'App:':<14}{data['app']}")

        if "name" in data:
            typer.echo(f"{'Migration:':<14}{data['name']}")

        if "dependencies" in data:
            typer.echo()
            typer.echo("Dependencies:")

            for dependency in data["dependencies"]:
                typer.echo(f"  • {dependency[0]}:{dependency[1]}")

        if "operations" in data:
            typer.echo()
            typer.echo("Operations:")

            for operation in data["operations"]:
                typer.echo(
                    f"  • {operation['operation']}"
                )

                details = operation.get("details", {})

                if details.get("model"):
                    typer.echo(
                        f"      Model: {details['model']}"
                    )

                if details.get("field"):
                    typer.echo(
                        f"      Field: {details['field']}"
                    )

        typer.echo()
        typer.echo("─" * 44)
    else:
        """Shows all the observations done by chronicle."""
        observations = ObservationRepo(conn).list_all()
        
        typer.echo()
        typer.echo("Chronicle Observations")
        typer.echo("─" * 75)
        typer.echo()

        if not observations:
            typer.echo("No observations found.")
            typer.echo()
            return

        typer.echo(
            f"{'ID':<5}"
            f"{'SOURCE':<12}"
            f"{'TYPE':<15}"
            f"EXTERNAL ID"
        )

        typer.echo("─" * 75)

        for observation in observations:
            formatted_external_id = observation.external_id[:7] if observation.source == "git" else observation.external_id
            
            typer.echo(
                f"{observation.id:<5}"
                f"{observation.source:<12}"
                f"{observation.type:<15}"
                f"{formatted_external_id}"
            )

        typer.echo()
        typer.echo("─" * 75)
        typer.echo(f"{len(observations)} observations")