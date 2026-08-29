from chronicle.interpretation.context import InterpretationContext
from chronicle.storage.models import Findings,Observation
from chronicle.project.discovery import find_project_root
from nltk.tokenize import word_tokenize
from pathlib import Path

STOP_WORDS = {"the","a","an","is","was","were","to","of","in","on","for","my","me","why","what","how","did","does","do","has","have","been","there",}

def build_context(
    question:str,
    findings: list[Findings],
    observations:list[Observation],
) -> InterpretationContext:
    
    keywords = _extract_keywords(question)
    scored_findings = []
    
    for finding in findings:
        score = _score_finding(
            finding,
            keywords,
        )
        
        if score > 0:
            scored_findings.append(
                (score, finding)
            )
        
    scored_findings.sort(
        key = lambda item: item[0],
        reverse=True
    )
    
    selected_findings = [
        finding for _, finding in scored_findings[:10]
    ]
    
    observation_map = {
        observation.id: observation for observation in observations
    }
    
    selected_observations = []
    
    for finding in selected_findings:
        observation = observation_map.get(finding.observation_id)
        
        if observation is not None:
            selected_observations.append(observation)
    
    related_observations = []
    
    for observation in selected_observations:
        related = _find_related_git_observations(
            observation,
            observations
        )
        
        related_observations.extend(related)

    selected_observations.extend(related_observations)
    
    unique_observations = {}
    
    for observation in selected_observations:
        unique_observations[observation.id] = observation
        
    selected_observations = list(unique_observations.values())
    
    return InterpretationContext(
        question=question,
        findings=selected_findings,
        observations=selected_observations,
    )
    
def _extract_keywords(question:str) -> list[str]:
    tokens = word_tokenize(question.lower())
    return [
        token for token in tokens if token.isalnum() and token not in STOP_WORDS and len(token) >= 3
    ]

def _finding_text(finding: Findings) -> str:
    return " ".join(
        [
            finding.title,
            finding.message,
            str(finding.data),
        ]
    ).lower()
    
def _score_finding(finding: Findings, keywords: list[str]) -> int:
    text = _finding_text(finding)
    score = 0
    
    for keyword in keywords:
        if keyword in finding.title.lower():
            score += 3
        if keyword in finding.message.lower():
            score += 2
        if keyword in str(finding.data).lower():
            score += 3
            
    return score

def _get_migration_path(observation: Observation) -> Path | None:
    project_root = find_project_root()
    if project_root is None:
        return None
    if observation.source != "django":
        return None
    if observation.type != "migration":
        return None
    
    root_name = project_root.name
    migration_name = observation.data.get("name")
    app_name = observation.data.get("app")
    if not migration_name:
        return None
    if not app_name:
        return None
    
    migration_file = migration_name + ".py"
    if app_name == root_name:
        return Path("migrations") / migration_file
     
    return Path(app_name) / "migrations" / migration_file

def _find_related_git_observations(migration: Observation, observations: list[Observation]) -> list[Observation]:
    migration_path = _get_migration_path(migration)
    
    if migration_path is None:
        return []
    
    related = []
    for observation in observations:
        if observation.source != "git":
            continue
        if observation.type != "commit":
            continue
        
        changes = observation.data.get("changes",[])
        
        for change in changes:
            if change.get("path") == str(migration_path):
                related.append(observation)
                break
            
    return related