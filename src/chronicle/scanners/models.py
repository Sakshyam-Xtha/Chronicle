from dataclasses import dataclass
from datetime import datetime

@dataclass
class Observation:
    source:str
    type:str 
    timestamp:datetime
    data:dict