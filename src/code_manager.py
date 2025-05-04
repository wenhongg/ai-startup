"""
Manages code changes and version control operations.
"""

import logging
from typing import Dict, Any, Optional
from github import Github
from .rate_limits import RateLimiter
from .config import settings
import time
import os
import re

class CodeManager:
    """Handles code changes and version control operations."""
    
    def __init__(self):
        """Initialize the code manager."""
        self.logger = logging.getLogger(__name__)
        self.github = Github(settings.github_token)
        self.rate_limiter = RateLimiter()
        
        # Extract owner/repo from the full URL
        match = re.match(r'https://github.com/([^/]+)/([^/]+)', settings.repo_url)
        if not match:
            raise ValueError(f"Invalid GitHub repository URL: {settings.repo_url}")
        owner, repo = match.groups()
        self.repo = self.github.get_repo(f"{owner}/{repo}")
    
    def create_pull_request(self, changes: Dict[str, Any], title: str, description: str) -> Optional[str]:
        """Create a pull request with rate limiting"""
        try:
            self.logger.info("Starting pull request creation process")
            self.logger.info(f"Title: {title}")
            self.logger.info(f"Description: {description}")
            self.logger.info(f"Number of files to modify: {len(changes)}")
            
            # Wait for GitHub rate limit
            self.logger.info("Checking GitHub rate limits...")
            self.rate_limiter.wait_if_needed("github")
            self.logger.info("Rate limit check passed")
            
            # Record GitHub request
            self.logger.info("Recording GitHub API request")
            self.rate_limiter.record_request("github")
            
            # Create new branch
            branch_name = f"ai-improvement-{int(time.time())}"
            self.logger.info(f"Creating new branch: {branch_name}")
            
            # Get the default branch
            default_branch = self.repo.default_branch
            self.logger.info(f"Default branch: {default_branch}")
            
            # Get the latest commit SHA from the default branch
            default_branch_ref = self.repo.get_git_ref(f"heads/{default_branch}")
            default_branch_sha = default_branch_ref.object.sha
            self.logger.info(f"Default branch SHA: {default_branch_sha}")
            
            # Create new branch from default branch
            self.repo.create_git_ref(f"refs/heads/{branch_name}", default_branch_sha)
            self.logger.info("Branch created successfully")
            
            # Apply changes
            self.logger.info("Applying changes to files...")
            for file_path, content in changes.items():
                self.logger.info(f"Modifying file: {file_path}")
                try:
                    # Get the current file content and SHA
                    file_content = self.repo.get_contents(file_path, ref=branch_name)
                    self.repo.update_file(
                        file_path,
                        f"AI Improvement: {title}",
                        content,
                        file_content.sha,
                        branch=branch_name
                    )
                except Exception as e:
                    if "404" in str(e):
                        # If file doesn't exist, create it
                        self.repo.create_file(
                            file_path,
                            f"AI Improvement: {title}",
                            content,
                            branch=branch_name
                        )
                    else:
                        raise
            self.logger.info("All files modified successfully")
            
            # Create pull request
            self.logger.info("Creating pull request...")
            pr = self.repo.create_pull(
                title=title,
                body=description,
                head=branch_name,
                base=default_branch
            )
            self.logger.info(f"Pull request created: {pr.html_url}")
            
            # Record GitHub completion
            self.logger.info("Recording GitHub API completion")
            self.rate_limiter.record_completion("github")
            
            self.logger.info(f"Pull request creation completed successfully. PR URL: {pr.html_url}")
            return pr.html_url
            
        except Exception as e:
            self.logger.error(f"Error creating pull request: {str(e)}")
            self.logger.error(f"Error details: {type(e).__name__}")
            raise
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get the current state of the codebase"""
        state = {}
        try:
            contents = self.repo.get_contents("")
            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(self.repo.get_contents(file_content.path))
                elif file_content.path.endswith('.py'):
                    state[file_content.path] = file_content.decoded_content.decode()
        except Exception as e:
            self.logger.error(f"Error getting current state: {str(e)}")
            raise
        return state
    
    def apply_changes(self, changes: Dict[str, Any], title: str, description: str) -> None:
        """Apply changes to the codebase"""
        try:
            # Apply changes
            for file_path, content in changes.items():
                with open(file_path, 'w') as f:
                    f.write(content)
            
            # Stage and commit changes
            self.repo.git.add('--all')
            self.repo.git.commit('-m', f'AI Improvement: {title}')
            
        except Exception as e:
            self.logger.error(f"Error applying changes: {str(e)}")
            raise 