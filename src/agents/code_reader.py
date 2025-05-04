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
from functools import lru_cache
import time
import backoff

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
            self.logger.error(f"Error loading prompt {filename}: {e}")
            return ""
    
    @backoff.on_exception(backoff.expo,
                          (Exception),  # Consider more specific exception types here
                          max_tries=3)
    def _generate_summary(self, prompt: str) -> str:
        """
        Generates a summary using the LLM, with retry logic.
        """
        try:
            return self.generate_response(prompt)
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}. Retrying...")
            raise  # Re-raise to trigger backoff

    @lru_cache(maxsize=128)
    def summarize(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Generate a concise summary of a code file.
        
        Args:
            file_path: Path to the file
            content: Content of the file
            
        Returns:
            Dictionary containing the summary and metadata
        """
        prompt_template = self._load_prompt("code_summary.txt")
        if not prompt_template:
            return {
                "file_path": file_path,
                "error": "Failed to load summary prompt."
            }

        prompt = prompt_template.format(
            file_path=file_path,
            content=content
        )
        
        try:
            summary = self._generate_summary(prompt)
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
                    summary = self.summarize(file_path, content)
                    # Check if summary exists in the result (it won't exist if summarization failed)
                    if "summary" in summary:
                        summaries.append(f"File: {file_path}\n{summary['summary']}\n")
            except Exception as e:
                self.logger.error(f"Error processing file {file_path}: {e}")
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

**Technical Analysis:**

The primary requirements involve implementing caching, improving the summary prompt, and adding error handling and retries to the `CodeReader` agent. The caching mechanism utilizes `functools.lru_cache` to store code summaries, keyed by file paths.  Error handling includes logging exceptions and retrying failed API calls using the `backoff` library. The code summarization prompt in `code_summary.txt` will be updated separately.

**Implementation Plan:**

1.  **Add `lru_cache` to `summarize`:** The `summarize` method is decorated with `@lru_cache(maxsize=128)` to enable caching of summaries. The cache key will be the file path.
2.  **Implement Retry Mechanism:** Implement retry logic using the `backoff` library. The `_generate_summary` function encapsulates the `generate_response` call and applies the retry decorator with exponential backoff.  This function is called by `summarize`.
3.  **Enhance Error Handling and Logging:** Improved error handling by logging errors using the `self.logger`.  Errors during prompt loading are also logged.
4.  **Testability:** The changes are designed to be testable with unit tests.

**Safety Considerations:**

1.  **Caching:** Caching can lead to stale summaries if the code changes frequently. The `maxsize` parameter of `lru_cache` limits the cache size. The system will regenerate summaries when the cache expires or is evicted.
2.  **Retries:** Retries can increase API costs if there are persistent errors.  The exponential backoff strategy limits the number of retries and the time spent retrying.

**Testing Approach:**

1.  **Unit Tests:**
    *   Test that the `summarize` method correctly uses the cache. Verify that the cache is populated and that subsequent calls with the same file path retrieve the summary from the cache.
    *   Test the retry mechanism. Mock the `generate_response` method to simulate API errors and verify that the retry logic is triggered and eventually succeeds (or fails after the maximum number of retries).
    *   Test that errors are logged correctly with appropriate error messages.
    *   Test that error cases in reading prompt files are handled.
2.  **Integration Tests:**  (Future - Consider adding integration tests)
    *   Ensure that the `CodeReader` integrates correctly with the `RepoReader`.

**Rollback Plan:**

1.  **Revert Changes:** In case of issues, the changes can be easily reverted by discarding the changes in the version control system.
2.  **Disable Caching (Temporarily):** If caching causes problems (e.g., stale data), the `@lru_cache` decorator can be removed temporarily to disable caching.
3.  **Disable Retries (Temporarily):** The `@backoff.on_exception` decorator can be removed from `_generate_summary` function to disable the retry mechanism.
