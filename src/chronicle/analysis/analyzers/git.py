from pathlib import Path

from chronicle.storage.models import Observation,Findings
from .base import BaseAnalyzer
from chronicle.analysis.context import AnalysisContext

class GitAnalyzer(BaseAnalyzer):
    def __init__(self, project_root: Path) -> None:
        super().__init__(project_root)
        
    def analyze(self,context:AnalysisContext) -> list[Findings]:
        findings = []
        for observation in context.observations:
            if observation.type != "commit":
                continue
            if observation.source != "git":
                continue

            message = observation.data.get("message","Not given")
            author = observation.data.get("author","unknown")
            parsed_message = author + ":" + message
            changes = observation.data.get("changes",[])
            
            for change in changes:
                file_status = change.get("status")
                if file_status == "A":
                    findings.append(
                        Findings(
                            analyzer="git_analyzer",
                            severity="info",
                            title="New File created",
                            message=parsed_message,
                            observation_id=observation.id, #type: ignore
                            data=change
                    ))
                    
        return findings