from dataclasses import dataclass, field

@dataclass
class ScanContext:
    state: dict[str,str | None] = field(
        default_factory=dict
    )
    
    def get_state(self,scanner:str,key:str) -> str |None:
        return self.state.get(f"{scanner}.{key}")