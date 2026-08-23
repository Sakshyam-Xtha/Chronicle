from dataclasses import dataclass
from datetime import datetime

@dataclass
class Observation:
    source:str
    type:str
    external_id:str 
    timestamp:datetime
    data:dict
    id:int | None = None