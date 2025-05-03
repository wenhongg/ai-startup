from ..agents.base import BaseAgent
from ..repo_reader import RepoReader
from ..config import settings
from typing import Dict, Any, List, Tuple, Optional

class DeveloperAI(BaseAgent):
    def __init__(self, repo_url: str):
        super().__init__()
        self.temperature = settings.temperature_developer
        self.system_prompt = self._load_prompt("developer.txt")
        self.repo_reader = RepoReader(repo_url)

    async def review_proposal(self, proposal: str) -> str:
        # Get all Python files from the repository
        files = self.repo_reader.get_python_files()
        
        # Analyze each file
        analysis_results = []
        for file in files:
            analysis = await self.analyze_code(file["content"])
            analysis_results.append({
                "file": file["path"],
                "analysis": analysis
            })
        
        # Then generate a response based on the analysis
        return await self.generate_response(
            "Review the following improvement proposal and create an implementation plan:",
            {
                "proposal": proposal,
                "files": files,
                "analysis": analysis_results
            }
        )

    async def implement_changes(self, plan: str) -> Tuple[Dict[str, Any], str, str]:
        """
        Implement the changes and generate pull request details
        Returns a tuple of (changes, title, description)
        """
        # Get all Python files from the repository
        files = self.repo_reader.get_python_files()
        
        # Analyze each file
        analysis_results = []
        for file in files:
            analysis = await self.analyze_code(file["content"])
            analysis_results.append({
                "file": file["path"],
                "analysis": analysis
            })
        
        response = await self.generate_response(
            "Implement the changes according to the following plan and provide a pull request title and description:",
            {
                "plan": plan,
                "files": files,
                "analysis": analysis_results,
                "instructions": """
                Please provide:
                1. The code changes for each file
                2. A clear, concise title for the pull request
                3. A detailed description including:
                   - What changes were made
                   - Why these changes are beneficial
                   - Any potential impacts
                   - Testing that was done
                """
            }
        )
        
        # Parse the response to extract changes, title, and description
        # This is a simplified version - you might want to add more robust parsing
        changes = {}  # This would be parsed from the response
        title = "AI-generated improvements"  # This would be parsed from the response
        description = response  # This would be parsed from the response
        
        return changes, title, description

    async def fix_issues(self, changes: Dict[str, Any], issues: List[str]) -> Tuple[Dict[str, Any], str, str]:
        """
        Fix issues found in the changes and return improved version with updated PR details
        Returns a tuple of (changes, title, description)
        """
        # Get all Python files from the repository
        files = self.repo_reader.get_python_files()
        
        # Analyze each file
        analysis_results = []
        for file in files:
            analysis = await self.analyze_code(file["content"])
            analysis_results.append({
                "file": file["path"],
                "analysis": analysis
            })
        
        response = await self.generate_response(
            "Fix the following issues in the changes:",
            {
                "changes": changes,
                "files": files,
                "analysis": analysis_results,
                "issues": issues
            }
        )
        
        # Parse the response to extract changes, title, and description
        # This is a simplified version - you might want to add more robust parsing
        fixed_changes = {}  # This would be parsed from the response
        title = "Fixed issues in AI-generated improvements"  # This would be parsed from the response
        description = response  # This would be parsed from the response
        
        return fixed_changes, title, description 