from dataclasses import dataclass,field

@dataclass
class AnalysisContext:
    state: dict[str,str | None] = field(
            default_factory=dict
        )
        
    def get_state(self,analyzer:str,obs_id:str) -> str |None:
            return self.state.get(f"{analyzer}.{obs_id}")