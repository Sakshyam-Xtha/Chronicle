from chronicle.ai.base import AIProvider
from chronicle.interpretation.context import InterpretationContext
from chronicle.interpretation.prompts import build_interpretation_prompt

class Interpreter:
    def __init__(self,provider: AIProvider) -> None:
        self.provider = provider
        
    def interpret(self, context: InterpretationContext) -> str:
        prompt = build_interpretation_prompt(context)
        
        return self.provider.generate(prompt)