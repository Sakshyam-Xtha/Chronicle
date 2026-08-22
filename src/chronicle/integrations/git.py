import subprocess
from pathlib import Path

class GitIntegration:
    def __init__(self,repo:Path) -> None:
        self.repo = repo
        
    def run(self, *arguments:str) -> str:
        result = subprocess.run(
            ["git", *arguments],
            cwd=self.repo,
            capture_output=True,
            check=True,
            text=True,
        )
        return result.stdout