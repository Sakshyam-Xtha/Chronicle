import typer
from chronicle.analysis.engine import AnalyzeEngine
from chronicle.analysis.analyzers.git import GitAnalyzer
from chronicle.config.loader import get_chronicle_directory
from chronicle.project.discovery import find_project_root
from chronicle.storage.database import connect
from chronicle.storage.observations import ObservationRepo
from chronicle.storage.findings import FindingsRepo
from chronicle.analysis.context import AnalysisContext
from chronicle.storage.analysis_state import AnalysisStateRepo

def analyze():
    """Analyzes all observations done by chronicle."""

    project_root = find_project_root()
    if project_root:
        db_path = (get_chronicle_directory(project_root) / "chronicle.db")
        conn = connect(db_path)
        observations = ObservationRepo(conn).list_all()
        analysis_state = AnalysisStateRepo(conn)
        last_obs_id = analysis_state.get(
            "last_observation_id",
            "analysis"
        )
        
        if last_obs_id is not None:
            observations = [
                observation for observation in observations if observation.id > int(last_obs_id) #type: ignore
            ]
            
        context = AnalysisContext(
            observations=observations,
            state={
                "analysis.last_observation_id":last_obs_id,
            }
        )
        
        repo = FindingsRepo(conn)
        analyzers = [
            GitAnalyzer(project_root),
        ]
        engine = AnalyzeEngine(analyzers) #type: ignore
        findings = engine.analyze(context)
        
        finding_count = 0
        
        with conn:
            for finding in findings:
                if repo.save(finding):
                    finding_count +=1
         
        if observations:
            newest_obs_id = max(
                observation.id for observation in observations
            ) 
            
            analysis_state.set(
                "last_observation_id",
                "analysis",
                str(newest_obs_id)
            )       
        typer.echo(f"Analyzed and stored {finding_count} findings.")
            