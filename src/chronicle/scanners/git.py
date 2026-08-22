import subprocess
from pathlib import Path
from datetime import datetime
from chronicle.integrations.git import GitIntegration
from .models import Observation
from .base import Scanner

class GitScanner(Scanner):
    """Scanner for Git repo history."""
    
    def __init__(self, project_root: Path) -> None:
        super().__init__(project_root)
        self.git = GitIntegration(project_root)
    
    def scan(self) -> list[Observation]:
        try:
            output = self.git.run(
                "log",
                "-1",
                "--format=%H|%aI|%s",
            )
        except subprocess.CalledProcessError:
            return []
        line = output.strip()
        if not line:
            return []
        
        commit_hash, timestamp, msg = line.split("|",2)
        observation = Observation(
            source="git",
            type="commit",
            timestamp=datetime.fromisoformat(timestamp),
            data={
                "hash":commit_hash,
                "message":msg
            }
        )
        return [observation]