from dataclasses import dataclass,field
from chronicle.storage.observations import Observation

@dataclass
class AnalysisContext:
    observations: list[Observation]
    state: dict[str,str | None] = field(
            default_factory=dict
        )
        
    def get_state(self,analyzer:str,key:str) -> str |None:
            return self.state.get(f"{analyzer}.{key}")