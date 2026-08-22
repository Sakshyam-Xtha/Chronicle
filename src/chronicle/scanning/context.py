from dataclasses import dataclass

@dataclass
class ScanContext:
    state: dict[str,str | None]