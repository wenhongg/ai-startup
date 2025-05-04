"""
Repository reader for accessing code from GitHub.
"""

from github import Github
from typing import List, Dict, Optional
from src.config import settings
import base64
import os

class RepoReader:
    """Handles reading code from GitHub repositories."""
    
    def __init__(self, repo_url: str, branch: str = "main"):
        """
        Initialize the repository reader.
        
        Args:
            repo_url: Full GitHub repository URL (e.g., 'https://github.com/username/repo')
            branch: Branch to read from (default: 'main')
        """
        self.github = Github(os.getenv("GITHUB_TOKEN"))
        self.repo_url = repo_url
        self.branch = branch
        
        # Extract owner and repo name from URL
        parts = repo_url.rstrip('/').split('/')
        self.owner = parts[-2]
        self.repo_name = parts[-1]
        
        # Get the repository
        self.repo = self.github.get_user(self.owner).get_repo(self.repo_name)
    
    def get_file_content(self, file_path: str) -> str:
        """
        Get the content of a file from the repository.
        
        Args:
            file_path: Path to the file in the repository
            
        Returns:
            File content as string
            
        Raises:
            Exception: If the file cannot be read or does not exist
        """
        try:
            content = self.repo.get_contents(file_path, ref=self.branch)
            if content.encoding == 'base64':
                return base64.b64decode(content.content).decode('utf-8')
            return content.content
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {str(e)}")

    def get_all_files(self, path: str = "") -> List[str]:
        """
        Get all filenames in the repository.
        
        Args:
            path: Starting path in the repository (default: root)
            
        Returns:
            List of file paths in the repository
            
        Raises:
            Exception: If there's an error accessing the repository
        """
        files = []
        try:
            contents = self.repo.get_contents(path, ref=self.branch)
            for content in contents:
                if content.type == "dir":
                    # Recursively get files from subdirectories
                    files.extend(self.get_all_files(content.path))
                else:
                    # Add file path to list
                    files.append(content.path)
        except Exception as e:
            raise Exception(f"Error getting files from {path}: {str(e)}")
        
        return files 