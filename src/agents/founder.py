from ..agents.base import BaseAgent

class FounderAI(BaseAgent):
    def __init__(self):
        super().__init__()
        self.temperature = self.settings.temperature_founder
        self.system_prompt = self._load_prompt("founder.txt")

    async def analyze_system(self) -> str:
        return await self.generate_response("Analyze the current state of the system and identify areas for improvement.")

    async def generate_proposal(self, analysis: str) -> str:
        return await self.generate_response(
            "Based on the following analysis, generate a detailed improvement proposal:",
            {"analysis": analysis}
        ) 