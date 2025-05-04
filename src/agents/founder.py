from ..agents.base import BaseAgent
from ..config import settings
from .code_reader import CodeReader

class FounderAI(BaseAgent):
    def __init__(self, code_reader: CodeReader):
        super().__init__()
        self.temperature = settings.temperature_founder
        self.code_reader = code_reader
        self.system_prompt = self._load_prompt("founder.txt")

    def generate_proposal(self, product_summaries: str) -> str:
        """Generate an improvement proposal based on the product information.
        
        Args:
            product_summaries: A comprehensive summary of the product codebase
            
        Returns:
            A detailed improvement proposal
        """
        prompt = f"""{self.system_prompt}

Product Information:
{product_summaries}

Based on the above information, please analyze the current state and propose improvements."""
        return self.generate_response(prompt=prompt) 