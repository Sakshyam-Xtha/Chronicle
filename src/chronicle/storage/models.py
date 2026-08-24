from dataclasses import dataclass,field
from datetime import datetime

@dataclass
class Observation:
    source:str
    type:str
    external_id:str 
    timestamp:datetime
    data:dict
    id:int | None = None
    
@dataclass
class Findings:
    analyzer: str
    severity: str
    title: str
    message: str
    observation_id: int
    data: dict = field(default_factory=dict)