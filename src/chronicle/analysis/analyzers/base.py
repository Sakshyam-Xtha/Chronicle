from abc import ABC,abstractmethod
from pathlib import Path
from chronicle.storage.models import Observation,Findings

class BaseAnalyzer(ABC):
    """Base class for all chronicle analyzers."""
        
    def __init__(self,project_root:Path) -> None:
        self.project_root = project_root
        
    @abstractmethod
    def analyze(self, observations:list[Observation]) -> list[Findings]:
        """Analyze the project and return findings."""
        pass