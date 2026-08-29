from openai import OpenAI
from chronicle.ai.base import AIProvider

class OpenAIProvider(AIProvider):
    def __init__(self,api_key:str,model:str) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
    def generate(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )
        return response.output_text