import git
import os
import logging
from typing import Dict, Any, Optional
import shutil
from datetime import datetime
from .observability import Observability
import asyncio
from git import Repo
from github import Github
from src.rate_limits import RateLimiter
import time

class CodeManager:
    def __init__(self, repo_path: str = "."):
        self.logger = logging.getLogger(__name__)
        self.repo_path = repo_path
        self.repo = Repo(repo_path)
        self.github = Github(os.getenv("GITHUB_TOKEN"))
        self.rate_limiter = RateLimiter()
        self.backup_dir = os.path.join(self.repo_path, "backups")
        os.makedirs(self.backup_dir, exist_ok=True)
        self.observability = Observability()
    
    async def create_pull_request(self, changes: Dict[str, Any], title: str, description: str) -> Optional[str]:
        """Create a pull request with rate limiting"""
        try:
            # Wait for GitHub rate limit
            await self.rate_limiter.wait_for_github()
            
            # Record GitHub request
            self.rate_limiter.record_github_request()
            
            # Create backup
            await self._create_backup()
            
            # Create and checkout new branch
            branch_name = f"ai-improvement-{int(time.time())}"
            self.repo.git.checkout('-b', branch_name)
            
            # Apply changes
            for file_path, content in changes.items():
                with open(file_path, 'w') as f:
                    f.write(content)
            
            # Stage and commit changes
            self.repo.git.add('--all')
            self.repo.git.commit('-m', f'AI Improvement: {title}')
            
            # Push changes
            self.repo.git.push('origin', branch_name)
            
            # Record GitHub completion
            self.rate_limiter.record_github_completion()
            
            return branch_name
            
        except Exception as e:
            self.logger.error(f"Error creating pull request: {str(e)}")
            await self._restore_backup()
            raise
    
    async def _create_backup(self) -> None:
        """Create a backup of the current state"""
        backup_path = os.path.join(
            self.backup_dir,
            f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        shutil.copytree(self.repo_path, backup_path, ignore=shutil.ignore_patterns('.git', 'backups'))
        self.logger.info(f"Created backup at {backup_path}")
    
    async def _restore_backup(self) -> None:
        """Restore the most recent backup"""
        try:
            backups = sorted(os.listdir(self.backup_dir))
            if not backups:
                self.logger.warning("No backups available to restore")
                return
            
            latest_backup = os.path.join(self.backup_dir, backups[-1])
            
            # Remove current files (except .git and backups)
            for item in os.listdir(self.repo_path):
                if item not in ['.git', 'backups']:
                    path = os.path.join(self.repo_path, item)
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
            
            # Copy backup files
            for item in os.listdir(latest_backup):
                src = os.path.join(latest_backup, item)
                dst = os.path.join(self.repo_path, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            
            self.logger.info(f"Restored backup from {latest_backup}")
            
        except Exception as e:
            self.logger.error(f"Error restoring backup: {str(e)}") 