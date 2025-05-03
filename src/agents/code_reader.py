"""
Code reader agent that specializes in summarizing code files.
"""

from typing import Dict, Any, List
import os
from .base import BaseAgent
from ..repo_reader import RepoReader
from ..config import settings

class CodeReader(BaseAgent):
    """Agent that reads and summarizes code files."""
    
    def __init__(self):
        """Initialize the code reader agent."""
        super().__init__()
        self.prompt_dir = os.path.join(os.path.dirname(__file__), "..", "prompts")
        self.repo_reader = RepoReader(settings.repo_url, settings.branch)
        
    def _load_prompt(self, filename: str) -> str:
        """Load a prompt from the prompts directory."""
        prompt_path = os.path.join(self.prompt_dir, filename)
        try:
            with open(prompt_path, "r") as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error loading prompt {filename}: {e}")
            return ""
        
    async def summarize(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Generate a concise summary of a code file.
        
        Args:
            file_path: Path to the file
            content: Content of the file
            
        Returns:
            Dictionary containing the summary and metadata
        """
        prompt_template = self._load_prompt("code_summary.txt")
        prompt = prompt_template.format(
            file_path=file_path,
            content=content
        )
        
        try:
            summary = await self.generate_response(prompt)
            return {
                "file_path": file_path,
                "summary": summary,
                "content": content
            }
        except Exception as e:
            print(f"Error summarizing file {file_path}: {e}")
            return {
                "file_path": file_path,
                "error": str(e)
            }

    async def summarize_repository(self) -> str:
        """
        Generate summaries for all files in the repository and concatenate them.
        
        Returns:
            String containing all file summaries
        """
        all_files = self.repo_reader.get_all_files()
        summaries = []
        
        for file_path in all_files:
            try:
                content = self.repo_reader.get_file_content(file_path)
                if content:
                    summary = await self.summarize(file_path, content)
                    # Check if summary exists in the result (it won't exist if summarization failed)
                    if "summary" in summary:
                        print(f"Summary: {summary['summary']}")
                        summaries.append(f"File: {file_path}\n{summary['summary']}\n")
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                summaries.append(f"File: {file_path}\nError: {str(e)}\n")
        
        return "\n".join(summaries) 