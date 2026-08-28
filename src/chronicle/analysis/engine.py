from pathlib import Path
from chronicle.analysis.context import AnalysisContext


from chronicle.analysis.analyzers.base import BaseAnalyzer
from chronicle.storage.models import Observation,Findings

class AnalyzeEngine:
    def __init__(self, analyzers:list[BaseAnalyzer]) -> None:
        self.analyzers = analyzers
        
    def analyze(self,context:AnalysisContext) -> list[Findings]:
        findings = []
        for analyzer in self.analyzers:
            analyzer_findings = analyzer.analyze(context)
            findings.extend(analyzer_findings)
            
        return findings