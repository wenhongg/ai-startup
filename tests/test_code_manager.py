```python
# src/orchestrator.py
import logging
import json
import time
import traceback
from functools import wraps
from typing import List, Dict, Any

from src.agents.agent import Agent, AgentOutput
from src.agents.code_reader import CodeReader
from src.agents.developer_ai import DeveloperAI
from src.agents.founder_ai import FounderAI
from src.code_manager import CodeManager
from src.safety_checker import SafetyChecker
from src.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SystemOrchestrator:
    def __init__(self, config: Config, code_manager: CodeManager, safety_checker: SafetyChecker,
                 founder_ai: FounderAI, developer_ai: DeveloperAI, code_reader: CodeReader):
        self.config = config
        self.code_manager = code_manager
        self.safety_checker = safety_checker
        self.founder_ai = founder_ai
        self.developer_ai = developer_ai
        self.code_reader = code_reader
        self.log_file = "orchestrator_log.jsonl"  # Use a JSONL file for structured logging
        self.log_entries = []

    def _log_entry(self, entry_type: str, details: Dict[str, Any]):
        log_entry = {
            "timestamp": time.time(),
            "type": entry_type,
            **details
        }
        self.log_entries.append(log_entry)
        self._write_log_entry(log_entry)

    def _write_log_entry(self, log_entry: Dict[str, Any]):
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write log entry: {e}")

    def _retry_api_call(self, func, *args, max_retries=3, base_delay=1, backoff_factor=2, **kwargs):
        """
        Retries an API call with exponential backoff.
        """
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries:
                    self._log_entry("error", {"message": f"API call failed after multiple retries: {e}", "function": func.__name__, "args": args, "kwargs": kwargs, "traceback": traceback.format_exc()})
                    raise  # Re-raise the exception after all retries
                delay = base_delay * (backoff_factor ** attempt)
                self._log_entry("warning", {"message": f"API call failed, retrying in {delay} seconds (attempt {attempt + 1}/{max_retries + 1}): {e}", "function": func.__name__, "args": args, "kwargs": kwargs, "traceback": traceback.format_exc()})
                time.sleep(delay)

    def _log_agent_communication(self, agent_name: str, communication_type: str, content: str):
        self._log_entry("agent_communication", {"agent": agent_name, "type": communication_type, "content": content})

    def run_improvement_cycle(self) -> None:
        """
        Orchestrates the improvement cycle, involving FounderAI and DeveloperAI.
        """
        try:
            # 1. Get Improvement Idea from FounderAI
            self._log_entry("step", {"description": "Getting improvement idea from FounderAI"})
            founder_output = self._retry_api_call(self.founder_ai.get_improvement_idea)
            self._log_agent_communication("FounderAI", "prompt", founder_output.prompt)
            self._log_agent_communication("FounderAI", "response", founder_output.response)

            if not founder_output.success:
                raise Exception(f"FounderAI failed to provide an improvement idea: {founder_output.error}")

            improvement_idea = founder_output.parsed_output

            # 2. DeveloperAI to Implement the Improvement
            self._log_entry("step", {"description": f"Implementing improvement: {improvement_idea}"})
            developer_output = self._retry_api_call(self.developer_ai.implement_improvement, improvement_idea)
            self._log_agent_communication("DeveloperAI", "prompt", developer_output.prompt)
            self._log_agent_communication("DeveloperAI", "response", developer_output.response)

            if not developer_output.success:
                raise Exception(f"DeveloperAI failed to implement the improvement: {developer_output.error}")

            # 3. Safety Checks and Code Manager
            self._log_entry("step", {"description": "Performing safety checks and applying code changes."})
            if not self.safety_checker.check_code_changes(developer_output.file_changes):
                raise Exception("Safety checks failed. Aborting code changes.")
            self.code_manager.apply_changes(developer_output.file_changes)

            # 4. Merge Changes (Optional, depends on DeveloperAI's output and CodeManager implementation)
            if developer_output.merge_request:
                self._log_entry("step", {"description": "Creating merge request."})
                self.code_manager.create_merge_request(developer_output.merge_request)
            self._log_entry("step", {"description": "Improvement cycle completed successfully."})

        except Exception as e:
            self._log_entry("error", {"message": f"An error occurred during the improvement cycle: {e}", "traceback": traceback.format_exc()})
            logger.error(f"An error occurred during the improvement cycle: {e}", exc_info=True)
            # Consider adding further error handling, such as sending notifications or attempting a rollback.


# src/agents/code_reader.py
import logging
import os
import functools
from typing import Dict, List
from src.config import Config
from src.llm_api_client import LLMAPIClient  # Assuming this is your LLM client
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CodeReader:
    def __init__(self, config: Config, llm_api_client: LLMAPIClient):
        self.config = config
        self.llm_api_client = llm_api_client
        self.cache_size = self.config.code_summary_cache_size
        self._summarize_code = functools.lru_cache(maxsize=self.cache_size)(self._summarize_code)

    def _get_file_content(self, file_path: str) -> str:
        """Reads the content of a file."""
        try:
            with open(file_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return ""
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return ""

    def _retry_api_call(self, func, *args, max_retries=3, base_delay=1, backoff_factor=2, **kwargs):
        """Retries an API call with exponential backoff."""
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"API call failed after multiple retries: {e}")
                    raise  # Re-raise the exception after all retries
                delay = base_delay * (backoff_factor ** attempt)
                logger.warning(f"API call failed, retrying in {delay} seconds (attempt {attempt + 1}/{max_retries + 1}): {e}")
                time.sleep(delay)

    def _summarize_code(self, file_path: str) -> str:
        """
        Summarizes the code in a given file using the LLM API.
        Uses the file path as the cache key.
        """
        file_content = self._get_file_content(file_path)
        if not file_content:
            return "Could not read file."

        prompt = self.config.code_summary_prompt.format(file_path=file_path, code=file_content)
        try:
            response = self._retry_api_call(self.llm_api_client.generate_text, prompt=prompt)
            if response:
                return response.strip()
            else:
                return "Could not generate summary."
        except Exception as e:
            logger.error(f"Error summarizing code for {file_path}: {e}")
            return "Error generating summary."

    def get_code_summary(self, file_path: str) -> str:
        """
        Retrieves the code summary, using the cache.
        """
        try:
            if not os.path.exists(file_path):
                return "File does not exist."
            summary = self._summarize_code(file_path)
            return summary
        except Exception as e:
            logger.error(f"Error getting code summary for {file_path}: {e}")
            return "Error retrieving summary."

    def clear_cache(self):
        """Clears the cache."""
        self._summarize_code.cache_clear()
        logger.info("Code summary cache cleared.")


# src/agents/developer_ai.py
import logging
from typing import List, Dict, Any
from src.agents.agent import Agent, AgentOutput
from src.config import Config
from src.llm_api_client import LLMAPIClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DeveloperAI(Agent):
    def __init__(self, config: Config, llm_api_client: LLMAPIClient):
        super().__init__(config=config, llm_api_client=llm_api_client)
        self.config = config
        self.llm_api_client = llm_api_client

    def implement_improvement(self, improvement_idea: str) -> AgentOutput:
        """
        Implements an improvement based on the given idea.
        Returns a dictionary containing file changes and a success flag.
        """
        prompt = self.config.developer_prompt.format(improvement_idea=improvement_idea)
        try:
            response = self.llm_api_client.generate_text(prompt=prompt)
            parsed_output = self._parse_developer_response(response)
            return AgentOutput(success=True, parsed_output=parsed_output, prompt=prompt, response=response)

        except Exception as e:
            logger.error(f"Error implementing improvement: {e}")
            return AgentOutput(success=False, error=str(e), prompt=prompt)

    def _parse_developer_response(self, response: str) -> Dict[str, Any]:
        """
        Parses the response from the DeveloperAI, extracting file changes.
        """
        # Placeholder for parsing logic.  This will need to be customized
        # based on the expected format of the DeveloperAI's output.
        # For example, it might look for JSON-formatted changes or
        # use regex to extract code blocks and file paths.

        file_changes = []
        merge_request = None
        try:
             # Assuming the response is JSON-formatted
            data = self._parse_json(response)
            if "file_changes" in data:
                file_changes = data["file_changes"]
            if "merge_request" in data:
                merge_request = data["merge_request"]

        except Exception as e:
            logger.error(f"Error parsing DeveloperAI response: {e}. Response: {response}")
            # Attempt to extract changes using a fallback mechanism (e.g., regex)
            # if the JSON parsing fails.  This is highly dependent on the
            # expected output format of the DeveloperAI.
            file_changes = self._extract_file_changes_fallback(response)  # Implement this
            if not file_changes:
                raise ValueError(f"Failed to parse DeveloperAI response even with fallback: {e}")


        return {"file_changes": file_changes, "merge_request": merge_request}

    def _extract_file_changes_fallback(self, response: str) -> List[Dict[str, str]]:
        """
        Fallback method to extract file changes using a less structured approach (e.g., regex).
        This is a placeholder and needs to be implemented based on the expected output format.
        """
        # Placeholder implementation - Replace with your actual parsing logic.
        # This example just returns an empty list to indicate no changes found.
        return []

    def _parse_json(self, text: str) -> Dict:
        """Parses a string as JSON.  Handles potential errors."""
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

# src/agents/founder_ai.py
import logging
from typing import Dict
from src.agents.agent import Agent, AgentOutput
from src.config import Config
from src.llm_api_client import LLMAPIClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FounderAI(Agent):
    def __init__(self, config: Config, llm_api_client: LLMAPIClient):
        super().__init__(config=config, llm_api_client=llm_api_client)
        self.config = config
        self.llm_api_client = llm_api_client

    def get_improvement_idea(self) -> AgentOutput:
        """
        Generates an improvement idea using the LLM.
        """
        prompt = self.config.founder_prompt
        try:
            response = self.llm_api_client.generate_text(prompt=prompt)
            parsed_output = self._parse_improvement_idea(response)
            return AgentOutput(success=True, parsed_output=parsed_output, prompt=prompt, response=response)

        except Exception as e:
            logger.error(f"Error getting improvement idea: {e}")
            return AgentOutput(success=False, error=str(e), prompt=prompt)


    def _parse_improvement_idea(self, response: str) -> str:
        """
        Parses the improvement idea from the response.  This is a placeholder
        and needs to be customized based on the expected output format
        of the FounderAI.
        """
        #  Example: Assuming the response is a simple text string.
        return response.strip()


# src/code_manager.py
import logging
import os
import shutil
from typing import List, Dict, Any
from src.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CodeManager:
    def __init__(self, config: Config):
        self.config = config

    def apply_changes(self, file_changes: List[Dict[str, Any]]) -> None:
        """Applies the given file changes to the codebase."""
        for change in file_changes:
            file_path = change.get("file_path")
            content = change.get("content")
            operation = change.get("operation", "replace")  # Default to 'replace'

            if not file_path or content is None:
                logger.warning(f"Invalid change: {change}. Skipping.")
                continue

            try:
                if operation == "replace":
                    self._replace_file_content(file_path, content)
                elif operation == "insert_before":
                    self._insert_before(file_path, content, change.get("marker"))
                elif operation == "insert_after":
                    self._insert_after(file_path, content, change.get("marker"))
                elif operation == "create":
                     self._create_file(file_path, content)
                elif operation == "delete":
                    self._delete_file(file_path)
                else:
                    logger.warning(f"Unsupported operation: {operation} for file {file_path}. Skipping.")
                    continue
            except Exception as e:
                logger.error(f"Error applying change to {file_path}: {e}")

    def _replace_file_content(self, file_path: str, content: str) -> None:
        """Replaces the entire content of a file."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write(content)
            logger.info(f"Replaced content of {file_path}")
        except Exception as e:
            logger.error(f"Error replacing content of {file_path}: {e}")
            raise

    def _insert_before(self, file_path: str, content: str, marker: str) -> None:
        """Inserts content before a specific marker in a file."""
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return

            with open(file_path, "r") as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                if marker in line:
                    lines.insert(i, content + "\n")
                    break
            else:
                logger.warning(f"Marker '{marker}' not found in {file_path}.  Skipping insert_before operation.")
                return

            with open(file_path, "w") as f:
                f.writelines(lines)
            logger.info(f"Inserted content before marker '{marker}' in {file_path}")
        except Exception as e:
            logger.error(f"Error inserting before marker in {file_path}: {e}")
            raise

    def _insert_after(self, file_path: str, content: str, marker: str) -> None:
        """Inserts content after a specific marker in a file."""
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return

            with open(file_path, "r") as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                if marker in line:
                    lines.insert(i + 1, content + "\n")
                    break
            else:
                logger.warning(f"Marker '{marker}' not found in {file_path}. Skipping insert_after operation.")
                return

            with open(file_path, "w") as f:
                f.writelines(lines)
            logger.info(f"Inserted content after marker '{marker}' in {file_path}")
        except Exception as e:
            logger.error(f"Error inserting after marker in {file_path}: {e}")
            raise

    def _create_file(self, file_path: str, content: str) -> None:
        """Creates a new file with the given content."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write(content)
            logger.info(f"Created file {file_path}")
        except Exception as e:
            logger.error(f"Error creating file {file_path}: {e}")
            raise

    def _delete_file(self, file_path: str) -> None:
        """Deletes a file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file {file_path}")
            else:
                logger.warning(f"File not found, cannot delete: {file_path}")
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            raise


    def create_merge_request(self, merge_request_details: Dict[str, Any]) -> None:
        """
        Creates a merge request (e.g., on GitHub, GitLab).
        This is a placeholder and needs to be implemented based on the specific
        version control system and API being used.
        """
        # Placeholder Implementation.
        # You will need to integrate with a version control system API here.
        # Example:  Using a hypothetical API client.

        try:
            title = merge_request_details.get("title", "Automated Code Changes")
            description = merge_request_details.get("description", "Automated changes by AI agent.")
            source_branch = merge_request_details.get("source_branch")
            target_branch = merge_request_details.get("target_branch", "main") # Or 'master' or whatever your main branch is.

            if not source_branch:
                raise ValueError("Source branch is required for creating a merge request.")

            # hypothetical API call:
            # api_client.create_merge_request(title=title, description=description, source_branch=source_branch, target_branch=target_branch)
            logger.info(f"Created merge request: Title: {title}, Source: {source_branch}, Target: {target_branch}")
            # Implement the API client integration
        except Exception as e:
            logger.error(f"Error creating merge request: {e}")
            raise


# src/safety_checker.py
import logging
import os
import re
from typing import List, Dict
from src.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SafetyChecker:
    def __init__(self, config: Config):
        self.config = config
        self.protected_patterns = self.config.protected_patterns
        self.protected_files = self.config.protected_files
        self.ai_maintained_files = self.config.ai_maintained_files

    def check_code_changes(self, file_changes: List[Dict]) -> bool:
        """
        Checks if the proposed file changes are safe.
        Returns True if the changes are safe, False otherwise.
        """
        for change in file_changes:
            file_path = change.get("file_path")
            content = change.get("content")
            operation = change.get("operation", "replace")

            if not file_path or content is None:
                logger.warning(f"Skipping safety checks for invalid change: {change}")
                continue

            if not self._is_file_allowed(file_path):
                logger.error(f"File {file_path} is not allowed for modification.")
                return False

            if operation == "replace":
                if not self._is_safe_replacement(file_path, content):
                    logger.error(f"Unsafe replacement detected in {file_path}")
                    return False
            elif operation == "insert_before" or operation == "insert_after":
                if not self._is_safe_insertion(file_path, content):
                     logger.error(f"Unsafe insertion detected in {file_path}")
                     return False
            elif operation == "create":
                if not self._is_safe_creation(file_path, content):
                    logger.error(f"Unsafe creation detected in {file_path}")
                    return False
            elif operation == "delete":
                if not self._is_safe_deletion(file_path):
                    logger.error(f"Unsafe deletion detected in {file_path}")
                    return False
            else:
                logger.warning(f"Unsupported operation {operation} for file {file_path}. Skipping safety check.")
                continue

        return True

    def _is_file_allowed(self, file_path: str) -> bool:
        """
        Checks if the file is allowed to be modified based on the configuration.
        """
        # Check if the file is explicitly protected.
        if file_path in self.protected_files:
            return False

        # Allow modifications to files maintained by the AI.
        if file_path in self.ai_maintained_files:
            return True

        # Otherwise, allow the modification
        return True

    def _is_safe_replacement(self, file_path: str, content: str) -> bool:
        """
        Checks if a file replacement is safe.
        """
        if not self._is_safe_content(content):
            return False
        return True

    def _is_safe_insertion(self, file_path: str, content: str) -> bool:
        """
        Checks if a file insertion is safe.
        """
        if not self._is_safe_content(content):
            return False
        return True

    def _is_safe_creation(self, file_path: str, content: str) -> bool:
        """
        Checks if a file creation is safe.
        """
        if not self._is_safe_content(content):
            return False
        return True

    def _is_safe_deletion(self, file_path: str) -> bool:
        """
        Checks if a file deletion is safe.  Currently, all deletions are allowed
        unless the file is explicitly protected.
        """
        if file_path in self.protected_files:
            return False
        return True


    def _is_safe_content(self, content: str) -> bool:
        """
        Checks if the content is safe based on the protected patterns.
        """
        if not content:
            return True  # Allow empty content

        for pattern in self.protected_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                logger.error(f"Safety check failed: Content matched protected pattern: {pattern}")
                return False
        return True

# src/config.py
import os
from typing import List, Dict, Any


class Config:
    def __init__(self):
        # LLM API Configuration (Example, adapt as needed)
        self.api_key = os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY") # Or other API key
        self.api_base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1") # Or other API base

        # Code Reader Configuration
        self.code_summary_cache_size = 128  # Adjust as needed

        # Prompts
        self.founder_prompt = """
        You are an AI that helps in software development by suggesting improvements.
        Suggest a single, specific improvement to be made to the codebase.
        Be concise and focus on actionable changes.  Do not include any code.
        """

        self.developer_prompt = """
        You are a Developer AI. You are given the following task: {improvement_idea}.
        Implement the improvement.  Provide file changes in the following format:
        ```json
        {{
          "file_changes": [
            {{
              "file_path": "path/to/file.py",
              "operation": "replace" | "insert_before" | "insert_after" | "create" | "delete",
              "content": "new content or code",
              "marker": "optional, for insert_before/after"
            }}
          ],
          "merge_request": {{
            "title": "Merge Request Title",
            "description": "Merge Request Description",
            "source_branch": "feature_branch_name"
          }}
        }}
        ```
        Ensure the file_path is relative to the project root.
        If no changes are needed, return an empty file_changes array.
        Only include file changes.  Do not include additional commentary.
        """

        self.code_summary_prompt = """
        You are a helpful coding assistant.  Summarize the following code, focusing on its purpose,
        functionality, and any key algorithms or data structures used.
        File Path: {file_path}
        Code:
        ```
        {code}
        ```
        Summary:
        """

        # Safety Configuration
        # Define patterns to prevent dangerous code modifications.
        # These are regular expressions.
        self.protected_patterns = [
            r"import\s+os",  # Prevent importing the 'os' module directly
            r"import\s+subprocess",  # Prevent importing subprocess
            r"open\(.+mode=['\"](w|a)",  # Prevent writing or appending to files directly
            r"shutil\.rmtree",  # Prevent recursive directory deletion
            r"eval\(",  # Prevent use of eval()
            r"exec\(",  # Prevent use of exec()
            r"import\s+sys.*sys\.exit\(", # Prevent sys.exit()
            r"import\s+.*pickle",  # Prevent potentially unsafe deserialization
            r"\(os\.(chmod|chown|chgrp)", # Prevent changing file permissions
            r"os\.system\(", # Prevent os.system calls
            r"subprocess\.call\(",  # Prevent subprocess calls
            r"subprocess\.run\(", # Prevent subprocess calls
            r"subprocess\.Popen\(", # Prevent subprocess calls
            r"open\(.+path=.*user_input", # Prevent use of user input in open
        ]

        # Files that should not be modified (absolute paths or relative to the project root).
        self.protected_files: List[str] = [
            "src/config.py", # Example: Protect the config file itself
            # Add more protected files here.  Use absolute paths or paths
            # relative to the project root.
        ]

        # Files that the AI is allowed to modify (relative to project root).
        self.ai_maintained_files: List[str] = [
            "src/agents/developer_ai.py",  # Example: AI can update itself
            # Add other files the AI is responsible for maintaining.
        ]

# src/llm_api_client.py
import os
import logging
import openai
from typing import Optional, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LLMAPIClient:
    def __init__(self, config: Config):
        self.config = config
        openai.api_key = self.config.api_key
        openai.api_base = self.config.api_base
        self.model = "gpt-3.5-turbo-1106"  # Or another suitable model.

    def generate_text(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> Optional[str]:
        """
        Generates text using the LLM API.
        """
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            return None
```

1.  **Technical Analysis of Requirements:**

    *   **Orchestrator Enhancement:**
        *   The primary focus is on improving the robustness of the `Orchestrator`.
        *   Implementation involves wrapping agent interactions and the `CodeManager` calls within `try-except` blocks.
        *   Error logging needs to include stack traces for detailed debugging.
        *   A retry mechanism with exponential backoff is required for API calls.
        *   All communication with AI agents needs to be logged.
        *   Impacts include increased logging and potential API cost increases if retries are frequent.
    *   **SafetyChecker Enhancement:**
        *   Requires expanding the `protected_patterns` in `src/safety_checker.py` to include more dangerous code patterns.
        *   Configuration of `protected_patterns`, `protected_files`, and `ai_maintained_files` needs to be moved to `src/config.py`.
        *   Impacts involve making the system more secure but potentially more restrictive.
    *   **CodeReader Optimization:**
        *   Implementation of `functools.lru_cache` for caching code summaries.
        *   Improving the prompt for better code summarization.
        *   Adding error handling and retries.
        *   Impacts include performance improvements, the risk of stale information, and potential API cost increases.
    *   **CodeManager Enhancement:**
        *   Adding functionality within `CodeManager` to perform merge request operations.
        *   Impact: enables the developer to fully automate merging processes, enabling more continuous integration and deployment.
    *   **Comprehensive Logging and Reporting:**
        *   Implementing structured (JSON formatted) logging for all steps, agents, prompts, responses, and actions.
        *   Impacts include increased storage costs and potential performance impact.
    *   **Code Quality:**
        *   Integration of linters (Black, isort, flake8, mypy) using pre-commit hooks.
        *   Impacts include increased development time for those not used to these tools, but it is a quality of life improvement for most.

2.  **Implementation Plan:**

    1.  **Backup:** Create a backup of the current code base before making any changes.
    2.  **Config.py Updates:**
        *   Move `protected_patterns`, `protected_files`, and `ai_maintained_files` to `src/config.py`.
        *   Instantiate the `Config` class in `src/orchestrator.py`, `src/code_reader.py`, `src/safety_checker.py`.
    3.  **SafetyChecker Implementation:**
        *   Update `src/safety_checker.py` to use the new config values.
        *   Expand `protected_patterns` in `src/config.py` with the additional checks.
    4.  **CodeReader Implementation:**
        *   Implement `functools.lru_cache` in `src/agents/code_reader.py`.
        *   Improve the code summarization prompt in `src/config.py`.
        *   Add error handling and retries in `src/agents/code_reader.py`.
    5.