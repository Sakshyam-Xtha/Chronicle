import typer
from chronicle.analysis.engine import AnalyzeEngine
from chronicle.analysis.analyzers.git import GitAnalyzer
from chronicle.config.loader import get_chronicle_directory
from chronicle.project.discovery import find_project_root
from chronicle.storage.database import connect
from chronicle.storage.observations import ObservationRepo
from chronicle.storage.findings import FindingsRepo
from dataclasses import asdict

def analyze():
    """Analyzes all observations done by chronicle."""

    project_root = find_project_root()
    if project_root:
        db_path = (get_chronicle_directory(project_root) / "chronicle.db")
        conn = connect(db_path)
        observations = ObservationRepo(conn).list_all()
        repo = FindingsRepo(conn)
        analyzers = [
            GitAnalyzer(project_root),
        ]
        engine = AnalyzeEngine(analyzers) #type: ignore
        findings = engine.analyze(observations)
        
        finding_count = 0
        
        with conn:
            for finding in findings:
                if repo.save(finding):
                    finding_count +=1
                
        typer.echo(f"Analyzed and stored {finding_count} findings.")
            