from abc import ABC, abstractmethod
from pathlib import Path

from .models import Observation

class Scanner(ABC):
    """Base class for all chronicle scanners."""
    
    def __init__(self,project_root:Path) -> None:
        self.project_root = project_root
        
    @abstractmethod
    def scan(self) -> list[Observation]:
        """Scan the project and return observation"""
        raise NotImplementedError