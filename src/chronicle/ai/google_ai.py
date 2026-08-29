from google import genai
from chronicle.ai.base import AIProvider

class GenAIProvider(AIProvider):
    def __init__(self,model:str,api_key:str) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model
        
    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents = prompt,
        )
        return response.text if response.text else "Error: Model did not respond"