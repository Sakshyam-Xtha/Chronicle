import subprocess
from pathlib import Path
from datetime import datetime
from chronicle.integrations.git import GitIntegration
from .models import Observation
from .base import Scanner
from chronicle.scanning.context import ScanContext

class GitScanner(Scanner):
    """Scanner for Git repo history."""
    
    def __init__(self, project_root: Path) -> None:
        super().__init__(project_root)
        self.git = GitIntegration(project_root)
    
    def scan(self,context:ScanContext) -> list[Observation]:
        last_commit = context.state.get("git.last_commit")
        try:
            if last_commit:
                output = self.git.run(
                    "log",
                    f"{last_commit}..HEAD",
                    "--format=%H|%aI|%s",
                )
            else:
                output = self.git.run(
                    "log",
                    "--format=%H|%aI|%s",
                )
        except subprocess.CalledProcessError:
            return []
        observation:list[Observation] = []
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            
            commit_hash, timestamp, msg = line.split("|",2)
            observation.append(Observation(
                source="git",
                type="commit",
                external_id=commit_hash,
                timestamp=datetime.fromisoformat(timestamp),
                data={
                    "hash":commit_hash,
                    "message":msg
                }
            ))
            
        return observation