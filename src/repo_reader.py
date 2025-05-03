"""
Repository reader for accessing code from GitHub.
"""

from github import Github
from typing import List, Dict, Optional
from src.config import settings
import base64

class RepoReader:
    """Handles reading code from GitHub repositories."""
    
    def __init__(self, repo_url: str, branch: str = "main"):
        """
        Initialize the repository reader.
        
        Args:
            repo_url: Full GitHub repository URL (e.g., 'https://github.com/username/repo')
            branch: Branch to read from (default: 'main')
        """
        self.github = Github(settings.github_token)
        self.repo_url = repo_url
        self.branch = branch
        
        # Extract owner and repo name from URL
        parts = repo_url.rstrip('/').split('/')
        self.owner = parts[-2]
        self.repo_name = parts[-1]
        
        # Get the repository
        self.repo = self.github.get_user(self.owner).get_repo(self.repo_name)
    
    def get_file_content(self, file_path: str) -> Optional[str]:
        """
        Get the content of a file from the repository.
        
        Args:
            file_path: Path to the file in the repository
            
        Returns:
            File content as string, or None if file not found
        """
        try:
            content = self.repo.get_contents(file_path, ref=self.branch)
            if content.encoding == 'base64':
                return base64.b64decode(content.content).decode('utf-8')
            return content.content
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def get_python_files(self, path: str = "") -> List[Dict[str, str]]:
        """
        Get all Python files in the repository.
        
        Args:
            path: Starting path in the repository (default: root)
            
        Returns:
            List of dictionaries containing file path and content
        """
        files = []
        try:
            contents = self.repo.get_contents(path, ref=self.branch)
            for content in contents:
                if content.type == "dir":
                    # Recursively get files from subdirectories
                    files.extend(self.get_python_files(content.path))
                elif content.path.endswith('.py'):
                    # Get file content
                    file_content = self.get_file_content(content.path)
                    if file_content:
                        files.append({
                            "path": content.path,
                            "content": file_content
                        })
        except Exception as e:
            print(f"Error getting files from {path}: {e}")
        
        return files
    
    def get_file_history(self, file_path: str, limit: int = 5) -> List[Dict[str, str]]:
        """
        Get the commit history for a file.
        
        Args:
            file_path: Path to the file in the repository
            limit: Maximum number of commits to return
            
        Returns:
            List of dictionaries containing commit messages and changes
        """
        history = []
        try:
            commits = self.repo.get_commits(path=file_path, sha=self.branch)
            for commit in commits[:limit]:
                history.append({
                    "sha": commit.sha,
                    "message": commit.commit.message,
                    "date": commit.commit.author.date.isoformat()
                })
        except Exception as e:
            print(f"Error getting history for {file_path}: {e}")
        
        return history

    def get_all_files(self, path: str = "") -> List[str]:
        """
        Get all filenames in the repository.
        
        Args:
            path: Starting path in the repository (default: root)
            
        Returns:
            List of file paths in the repository
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
                    print(f"File: {content.path}")
                    files.append(content.path)
        except Exception as e:
            print(f"Error getting files from {path}: {e}")
        
        return files 