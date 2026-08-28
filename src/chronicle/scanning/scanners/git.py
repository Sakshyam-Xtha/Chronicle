import subprocess
from pathlib import Path
from datetime import datetime
from chronicle.integrations.git import GitIntegration
from ...storage.models import Observation
from .git_models import FileChange
from .base import Scanner
from chronicle.scanning.context import ScanContext

class GitScanner(Scanner):
    """Scanner for Git repo history."""
    
    def __init__(self, project_root: Path) -> None:
        super().__init__(project_root)
        self.git = GitIntegration(project_root)
    
    def scan(self,contexts:list[ScanContext]) -> list[Observation]:
        for context in contexts:
            last_commit = context.get_state("git","last_commit")
            if last_commit:
                break
        try:
            if last_commit:
                output = self.git.run(
                    "log",
                    f"{last_commit}..HEAD",
                    "--format=%H|%P|%aI|%an|%s",
                )
            else:
                output = self.git.run(
                    "log",
                    "--format=%H|%P|%aI|%an|%s",
                )
        except subprocess.CalledProcessError:
            return []
        observation:list[Observation] = []
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            
            commit_hash, parents, timestamp, author, msg = line.split("|",4)
            
            parents_hash = parents.split() if parents else []
            
            changes = self.get_changed_file(commit_hash=commit_hash)
            
            observation.append(Observation(
                source="git",
                type="commit",
                external_id=commit_hash,
                timestamp=datetime.fromisoformat(timestamp),
                data={
                    "hash":commit_hash,
                    "message":msg,
                    "author":author,
                    "parents":parents_hash,
                    "changes": [
                        {
                            "path": change.path,
                            "status": change.status,
                        }
                        for change in changes
                    ]
                }
            ))
            
        return observation
    
    def get_changed_file(self,commit_hash:str) -> list[FileChange]:
        changes_observed = self.git.run(
            "diff-tree",
            "--no-commit-id",
            "--name-status",
            "-r",
            commit_hash,
        )
        
        changes = []
        for line in changes_observed.splitlines():
            line = line.strip()
            if not line:
                continue
            
            status, path = line.split("\t", 1)

            changes.append(
                FileChange(
                    path=path,
                    status=status,
                )
            )
            
        return changes