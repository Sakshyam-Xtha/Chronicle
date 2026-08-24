from dataclasses import dataclass

@dataclass
class FileChange:
    path:str
    status:str