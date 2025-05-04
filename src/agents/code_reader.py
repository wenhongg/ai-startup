```python
"""
Code reader agent that specializes in summarizing code files.
"""

from typing import Dict, Any, List, Optional
import os
import logging
from .base import BaseAgent
from ..repo_reader import RepoReader
from ..config import settings
from github import Github

class CodeReader(BaseAgent):
    """Agent that reads and summarizes code files."""
    
    def __init__(self):
        """Initialize the code reader agent."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.prompt_dir = os.path.join(os.path.dirname(__file__), "..", "prompts")
        self.repo_reader = RepoReader(settings.repo_url, settings.branch)
        self._cached_summaries = None
        self.github = Github(os.getenv("GITHUB_TOKEN"))
        
        # Extract owner/repo from the full URL
        import re
        match = re.match(r'https://github.com/([^/]+)/([^/]+)', settings.repo_url)
        if not match:
            raise ValueError(f"Invalid GitHub repository URL: {settings.repo_url}")
        owner, repo = match.groups()
        self.repo = self.github.get_repo(f"{owner}/{repo}")
        
    def _load_prompt(self, filename: str) -> str:
        """Load a prompt from the prompts directory."""
        prompt_path = os.path.join(self.prompt_dir, filename)
        try:
            with open(prompt_path, "r") as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error loading prompt {filename}: {e}")
            return ""
        
    def summarize(self, file_path: str, content: str, file_type: str) -> Dict[str, Any]:
        """
        Generate a concise summary of a code file.
        
        Args:
            file_path: Path to the file
            content: Content of the file
            file_type: Type of the file (e.g., "Python", "JavaScript")
            
        Returns:
            Dictionary containing the summary and metadata
        """
        prompt_template = self._load_prompt("code_summary.txt")
        prompt = prompt_template.format(
            file_path=file_path,
            content=content,
            file_type=file_type
        )
        
        try:
            summary = self.generate_response(prompt)
            return {
                "file_path": file_path,
                "summary": summary,
                "content": content
            }
        except Exception as e:
            self.logger.error(f"Error summarizing file {file_path}: {e}")
            return {
                "file_path": file_path,
                "error": str(e)
            }

    def summarize_repository(self) -> None:
        """
        Generate summaries for all files in the repository and store them.
        """
        all_files = self.repo_reader.get_all_files()
        summaries = []
        
        for file_path in all_files:
            try:
                content = self.repo_reader.get_file_content(file_path)
                if content:
                    file_type = file_path.split('.')[-1].capitalize()
                    summary = self.summarize(file_path, content, file_type)
                    # Check if summary exists in the result (it won't exist if summarization failed)
                    if "summary" in summary:
                        summaries.append(f"File: {file_path}\n{summary['summary']}\n")
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                summaries.append(f"File: {file_path}\nError: {str(e)}\n")
        
        self._cached_summaries = "\n".join(summaries)

    def get_code_summaries(self) -> str:
        """
        Get the cached code summaries. If not available, generate them first.
        
        Returns:
            String containing all file summaries
        """
        if self._cached_summaries is None:
            self.summarize_repository()
        return self._cached_summaries

    def reset(self) -> None:
        """
        Reset the code reader by clearing all caches.
        This includes:
        - File content cache in repo_reader
        - Cached code summaries
        """
        self.repo_reader.reset()
        self._cached_summaries = None

    def read_file(self, file_path: str) -> str:
        """Read the contents of a file from the repository.
        
        Args:
            file_path: Path to the file relative to the repository root
            
        Returns:
            The contents of the file as a string, or empty string if file doesn't exist
            
        Raises:
            Exception: If there's an error other than file not found
        """
        try:
            content = self.repo_reader.get_file_content(file_path)
            if content is None:
                self.logger.warning(f"File not found: {file_path}")
                return ""
            return content
        except Exception as e:
            if "404" in str(e):
                self.logger.warning(f"File not found: {file_path}")
                return ""
            self.logger.error(f"Error reading file {file_path}: {str(e)}")
            raise
```