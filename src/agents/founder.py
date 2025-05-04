from ..agents.base import BaseAgent
from ..config import settings
from .code_reader import CodeReader

class FounderAI(BaseAgent):
    def __init__(self, code_reader: CodeReader):
        super().__init__()
        self.temperature = settings.temperature_founder
        self.code_reader = code_reader
        self.system_prompt = self._load_prompt("founder.txt")
        self._cached_proposal = None

    def generate_proposal(self, product_summaries: str) -> str:
        """Generate an improvement proposal based on the product information.
        
        Args:
            product_summaries: A comprehensive summary of the product codebase
            
        Returns:
            A detailed improvement proposal
        """
        # Check cache first
        if self._cached_proposal is not None:
            return self._cached_proposal

        prompt = f"""{self.system_prompt}

Product Information:
{product_summaries}

Based on the above information, please analyze the current state and propose a single improvement and elaborate on it."""

        proposal = self.generate_response(prompt=prompt)
        self._cached_proposal = proposal
        return proposal

    def get_cached_proposal(self) -> str:
        """Get the cached proposal if available.
        
        Returns:
            The cached proposal, or None if no proposal has been generated yet
        """
        return self._cached_proposal

    def reset(self):
        """Clear the cached proposal."""
        self._cached_proposal = None 