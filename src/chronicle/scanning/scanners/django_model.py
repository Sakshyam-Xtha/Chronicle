from dataclasses import dataclass

@dataclass
class MigrationOperation:
    operation:str
    details:dict
    
    def to_dict(self) -> dict:
        return {
            "operation":self.operation,
            "details":self.details
        }