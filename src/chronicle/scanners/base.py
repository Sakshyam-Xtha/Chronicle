from abc import ABC, abstractmethod
from pathlib import Path

from .models import Observation
from chronicle.scanning.context import ScanContext

class Scanner(ABC):
    """Base class for all chronicle scanners."""
    
    def __init__(self,project_root:Path) -> None:
        self.project_root = project_root
        
    @abstractmethod
    def scan(self,context:ScanContext) -> list[Observation]:
        """Scan the project and return observation"""
        pass