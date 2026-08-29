from chronicle.interpretation.context import InterpretationContext

def build_interpretation_prompt(context: InterpretationContext) -> str:
    prompt = f"""
You are Chronicle, a software project history interpreter.

Answer the user's question using only the project history
provided below.

User question:
{context.question}

Findings:
"""

    for finding in context.findings:
        prompt += f"""
- Analyzer: {finding.analyzer}
- Severity: {finding.severity}
- Title: {finding.title}
- Message: {finding.message}
- Observation ID: {finding.observation_id}
- Data: {finding.data}
"""

    prompt += """

Observations:
"""

    for observation in context.observations:
        prompt += f""" 
- ID: {observation.id}
- Source: {observation.source}
- Type: {observation.type}
- External ID: {observation.external_id}
- Timestamp: {observation.timestamp}
- Data: {observation.data}
"""

    prompt += """

Explain what happened, why it happened, and what effect it
may have on the project.

If the provided project history does not contain enough
information to answer the question, say so instead of
inventing information.   
"""

    return prompt