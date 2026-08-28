from abc import ABC,abstractmethod
from pathlib import Path
from chronicle.storage.models import Observation,Findings
from chronicle.analysis.context import AnalysisContext

class BaseAnalyzer(ABC):
    """Base class for all chronicle analyzers."""
        
    def __init__(self,project_root:Path) -> None:
        self.project_root = project_root
        
    @abstractmethod
    def analyze(self, context:AnalysisContext) -> list[Findings]:
        """Analyze the project and return findings."""
        pass