from pathlib import Path

from chronicle.storage.models import Observation,Findings
from .base import BaseAnalyzer

class GitAnalyzer(BaseAnalyzer):
    def __init__(self, project_root: Path) -> None:
        super().__init__(project_root)
        
    def analyze(self,observations:list[Observation]) -> list[Findings]:
        findings = []
        for observation in observations:
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