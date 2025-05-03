from ..agents.base import BaseAgent
from ..config import settings
from ..repo_reader import RepoReader
from .code_reader import CodeReader

class FounderAI(BaseAgent):
    def __init__(self):
        super().__init__()
        self.temperature = settings.temperature_founder
        self.repo_reader = RepoReader(settings.repo_url, settings.branch)
        self.code_reader = CodeReader()
        self.system_prompt = None  # Will be set in initialize()

    async def initialize(self):
        """Initialize the founder AI with product summaries."""
        self.system_prompt = self._load_prompt("founder.txt").format(
            product_summaries=await self._get_product_summaries()
        )

    async def _get_product_summaries(self) -> str:
        """Get a comprehensive summary of the product."""
        return await self.code_reader.summarize_repository()

    async def generate_proposal(self) -> str:
        return await self.generate_response(
            prompt="Generate a detailed improvement proposal based on the product information."
        ) 