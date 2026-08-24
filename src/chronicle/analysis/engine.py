from pathlib import Path
from .analyzers.base import BaseAnalyzer
from chronicle.storage.models import Observation,Findings

class AnalyzeEngine:
    def __init__(self, analyzers:list[BaseAnalyzer]) -> None:
        self.analyzers = analyzers
        
    def analyze(self,observations:list[Observation]) -> list[Findings]:
        findings = []
        for analyzer in self.analyzers:
            analyzer_findings = analyzer.analyze(observations)
            findings.extend(analyzer_findings)
            
        return findings