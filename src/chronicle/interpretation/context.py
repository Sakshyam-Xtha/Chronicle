from dataclasses import dataclass
from chronicle.storage.models import Findings,Observation

@dataclass
class InterpretationContext:
    question: str
    findings: list[Findings]
    observations: list[Observation]