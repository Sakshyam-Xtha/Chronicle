from pathlib import Path
from chronicle.scanners.base import Scanner
from chronicle.scanners.models import Observation

class ScanEngine:
    def __init__(self,project_root:Path,scanners:list[Scanner]) -> None:
        self.project_root = project_root
        self.scanners = scanners
        
    def scan(self) -> list[Observation]:
        observation:list[Observation] = []
        for scanner in self.scanners:
            observation.extend(scanner.scan())
        
        return observation