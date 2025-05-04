```python
# src/orchestrator.py
import logging
import time
import traceback
from functools import partial
from typing import Callable, Dict, List, Optional, Tuple, Union

from src.agents.agent import Agent, AgentAction, AgentResponse
from src.code_manager import CodeManager
from src.config import Config
from src.safety_checker import SafetyChecker

logger = logging.getLogger(__name__)

class SystemOrchestrator:
    """
    Orchestrates the interaction between AI agents and the codebase.
    Manages the improvement cycle, safety checks, and code updates.
    """

    def __init__(
        self,
        config: Config,
        code_manager: CodeManager,
        safety_checker: SafetyChecker,
        agents: Dict[str, Agent],
    ):
        self.config = config
        self.code_manager = code_manager
        self.safety_checker = safety_checker
        self.agents = agents
        self.error_log = []
        self.agent_communication_log = []

    def _log_agent_interaction(self, agent_name: str, prompt: str, response: str):
        """Logs the communication between the orchestrator and an agent."""
        log_entry = {
            "timestamp": time.time(),
            "agent_name": agent_name,
            "prompt": prompt,
            "response": response,
        }
        self.agent_communication_log.append(log_entry)
        logger.debug(f"Agent Communication - Agent: {agent_name}, Prompt: {prompt}, Response: {response}")

    def _retry_with_backoff(
        self,
        func: Callable,
        *args,
        retries: int = 3,
        backoff_factor: float = 1.0,
        **kwargs,
    ):
        """Retries a function with exponential backoff."""
        for attempt in range(retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == retries:
                    logger.error(f"Function {func.__name__} failed after {retries} retries: {e}")
                    raise
                else:
                    wait_time = backoff_factor * (2 ** attempt)
                    logger.warning(
                        f"Function {func.__name__} failed, retrying in {wait_time:.2f} seconds... Attempt {attempt + 1}/{retries+1}: {e}"
                    )
                    time.sleep(wait_time)

    def run_improvement_cycle(self) -> bool:
        """
        Runs a single improvement cycle.
        1.  Gets a task from Founder AI
        2.  Gets code changes from Developer AI based on task
        3.  Validates the changes with SafetyChecker
        4.  Applies the changes using CodeManager
        """
        try:
            task = self._retry_with_backoff(self._get_task_from_founder_ai)
            if not task:
                logger.info("No task received from Founder AI.")
                return False

            logger.info(f"Received task from Founder AI: {task}")
            self._log_step(f"Received task from Founder AI: {task}")

            developer_response = self._retry_with_backoff(
                self._get_code_changes_from_developer_ai, task
            )
            if not developer_response:
                logger.warning("No code changes received from Developer AI.")
                return False

            logger.info(f"Received code changes from Developer AI: {developer_response}")
            self._log_step(f"Received code changes from Developer AI: {developer_response}")

            if not self.safety_checker.is_safe(
                developer_response.get("changes", [])
            ):
                logger.error("Safety check failed.  Changes not applied.")
                self.error_log.append(
                    {
                        "message": "Safety check failed",
                        "changes": developer_response.get("changes", []),
                    }
                )
                self._log_step("Safety check failed. Changes not applied.")
                return False

            if not self.code_manager.apply_changes(developer_response.get("changes", [])):
                logger.error("Failed to apply changes.")
                self.error_log.append(
                    {
                        "message": "Failed to apply changes.",
                        "changes": developer_response.get("changes", []),
                    }
                )
                self._log_step("Failed to apply changes.")
                return False
            self._log_step("Changes applied successfully.")
            return True

        except Exception as e:
            logger.error(f"An unexpected error occurred in run_improvement_cycle: {e}")
            logger.error(traceback.format_exc())
            self.error_log.append(
                {
                    "message": "An unexpected error occurred.",
                    "exception": str(e),
                    "traceback": traceback.format_exc(),
                }
            )
            self._log_step("An unexpected error occurred during the improvement cycle.")
            return False

    def _get_task_from_founder_ai(self) -> Optional[str]:
        """Gets a task from the Founder AI agent."""
        try:
            agent = self.agents["FounderAI"]
            prompt = "Please provide a task to improve the codebase."
            self._log_agent_interaction("FounderAI", prompt, "")  # Log the prompt first
            response: AgentResponse = agent.get_response(prompt)
            self._log_agent_interaction("FounderAI", prompt, response.content)  # Log the response
            return response.content
        except Exception as e:
            logger.error(f"Error getting task from Founder AI: {e}")
            logger.error(traceback.format_exc())
            raise  # Re-raise to be caught by retry mechanism

    def _get_code_changes_from_developer_ai(self, task: str) -> Optional[Dict]:
        """Gets code changes from the Developer AI agent."""
        try:
            agent = self.agents["DeveloperAI"]
            prompt = f"Task: {task}\n\nPlease provide code changes to address the task.  Respond with a JSON object containing a 'changes' key, which is a list of file changes.  Each change should contain 'file_path' and 'content' keys.  Example: {{\n  'changes': [\n    {{\n      'file_path': 'src/example.py',\n      'content': 'def new_function():\\n    pass'\n    }}\n  ]\n}}"
            self._log_agent_interaction("DeveloperAI", prompt, "")  # Log the prompt first
            response: AgentResponse = agent.get_response(prompt)
            self._log_agent_interaction("DeveloperAI", prompt, response.content)  # Log the response
            return response.json_content
        except Exception as e:
            logger.error(f"Error getting code changes from Developer AI: {e}")
            logger.error(traceback.format_exc())
            raise  # Re-raise to be caught by retry mechanism

    def _log_step(self, message: str):
        """Logs a step in the process."""
        logger.info(f"Step: {message}")
        # In a real implementation, you would likely add structured logging here
        # using a library like `structlog` or `loguru`.  For example:
        # logger.info("step", message=message)

    def get_error_log(self) -> List[Dict]:
        return self.error_log

    def get_agent_communication_log(self) -> List[Dict]:
        return self.agent_communication_log
```

```python
# src/safety_checker.py
import logging
import re
from typing import List, Dict

from src.config import Config

logger = logging.getLogger(__name__)


class SafetyChecker:
    """
    Checks the safety of code changes.
    """

    def __init__(self, config: Config):
        self.config = config
        self.protected_files = config.protected_files
        self.ai_maintained_files = config.ai_maintained_files
        self.protected_patterns = config.protected_patterns

    def is_safe(self, changes: List[Dict]) -> bool:
        """
        Checks if a list of code changes is safe.
        """
        for change in changes:
            file_path = change.get("file_path")
            content = change.get("content")
            if not file_path or content is None:
                logger.warning(f"Skipping safety check for change due to missing file_path or content: {change}")
                continue

            if not self._is_file_safe(file_path):
                logger.error(f"File {file_path} is not safe for modification.")
                return False

            if not self._is_content_safe(content):
                logger.error(f"Content for {file_path} is not safe.")
                return False

        return True

    def _is_file_safe(self, file_path: str) -> bool:
        """
        Checks if a file is safe to modify based on configuration.
        """
        if file_path in self.protected_files:
            logger.error(f"File {file_path} is protected and cannot be modified.")
            return False

        if not self.config.allow_all_file_changes and file_path not in self.ai_maintained_files:
            logger.error(f"File {file_path} is not in the allowed list and cannot be modified.")
            return False

        return True


    def _is_content_safe(self, content: str) -> bool:
        """
        Checks if the content is safe based on regex patterns.
        """
        if not content:
            return True

        for pattern in self.protected_patterns:
            if re.search(pattern, content, re.DOTALL):
                logger.error(f"Content contains a disallowed pattern: {pattern}")
                return False
        return True
```

```python
# src/agents/code_reader.py
import logging
import os
import functools
from typing import Dict

from src.agents.agent import Agent, AgentAction, AgentResponse
from src.config import Config

logger = logging.getLogger(__name__)


class CodeReader:
    """
    Reads and summarizes code files.
    """

    def __init__(self, config: Config, agent: Agent):
        self.config = config
        self.agent = agent

    @functools.lru_cache(maxsize=128)  # Cache up to 128 summaries
    def summarize_code(self, file_path: str) -> str:
        """
        Summarizes the code in a given file. Uses caching to avoid redundant summarization calls.
        """
        try:
            with open(file_path, "r") as f:
                code = f.read()
            if not code:
                return "File is empty."

            prompt = (
                f"Summarize the following code concisely.  Provide a brief overview "
                f"of the code's functionality, key classes, and methods. Focus "
                f"on what the code *does*, not just what it *is*. Code:\n\n{code}"
            )
            response: AgentResponse = self.agent.get_response(prompt)
            summary = response.content
            logger.debug(f"Summarized {file_path}: {summary}")  # Log the summary for debugging
            return summary
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return "File not found."
        except Exception as e:
            logger.error(f"Error summarizing {file_path}: {e}")
            return "Error summarizing code."
```

```python
# src/code_manager.py
import logging
import os
from typing import List, Dict

logger = logging.getLogger(__name__)


class CodeManager:
    """
    Manages the codebase, including applying changes and creating merge requests.
    """

    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def apply_changes(self, changes: List[Dict]) -> bool:
        """
        Applies a list of code changes to the codebase.
        """
        try:
            for change in changes:
                file_path = change.get("file_path")
                content = change.get("content")
                if not file_path or content is None:
                    logger.warning(f"Skipping change due to missing file_path or content: {change}")
                    continue

                full_path = os.path.join(self.repo_path, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)  # Ensure directory exists

                with open(full_path, "w") as f:
                    f.write(content)
                logger.info(f"Applied change to {file_path}")

            return True

        except Exception as e:
            logger.error(f"Error applying changes: {e}")
            return False

    def create_merge_request(self, branch_name: str, title: str, description: str) -> bool:
        """
        Creates a merge request for the changes.
        """
        # This is a placeholder.  In a real implementation,
        # this would interact with a version control system like Git
        # to create a merge request.
        logger.info(
            f"Creating merge request: Branch: {branch_name}, Title: {title}, Description: {description}"
        )
        # Simulate a merge request creation
        print(f"Simulated merge request created: {title}")
        return True
```

```python
# src/config.py
import os
from typing import List, Dict

class Config:
    """
    Configuration for the AI system.
    """
    def __init__(self):
        # File paths and patterns - Moved from SafetyChecker
        self.protected_files: List[str] = [
            "src/config.py",
            "src/safety_checker.py",
            "src/orchestrator.py",
        ]
        self.ai_maintained_files: List[str] = []  # Files AI is allowed to modify

        # Regex patterns to prevent dangerous code - Moved from SafetyChecker
        self.protected_patterns: List[str] = [
            r"import os",
            r"import shutil",
            r"subprocess\.run",
            r"open\(.*, *[\"']w",  # open for writing
            r"open\(.*, *[\"']a",  # open for appending
            r"\.\.remove",
            r"\.\.unlink",
            r"rmdir",
            r"shutil\.rmtree",
            r"eval\(",
            r"exec\(",
            r"import * as os",
            r"import * as shutil",
        ]
        self.allow_all_file_changes: bool = False # false to only allow ai_maintained_files to be changed.
```

```python
# tests/test_orchestrator.py
import unittest
from unittest.mock import MagicMock, patch

from src.orchestrator import SystemOrchestrator
from src.config import Config
from src.code_manager import CodeManager
from src.safety_checker import SafetyChecker
from src.agents.agent import Agent, AgentResponse


class TestSystemOrchestrator(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.code_manager = CodeManager(repo_path="./")  # Use a dummy repo path
        self.safety_checker = SafetyChecker(self.config)
        self.founder_ai_mock = MagicMock(spec=Agent)
        self.developer_ai_mock = MagicMock(spec=Agent)
        self.agents = {
            "FounderAI": self.founder_ai_mock,
            "DeveloperAI": self.developer_ai_mock,
        }
        self.orchestrator = SystemOrchestrator(
            self.config, self.code_manager, self.safety_checker, self.agents
        )

    @patch("src.orchestrator.logger.error")
    def test_run_improvement_cycle_success(self, mock_logger_error):
        """Test a successful improvement cycle."""
        task = "Improve the documentation."
        code_changes = [{"file_path": "README.md", "content": "# My Project"}]
        founder_response = AgentResponse(content=task)
        developer_response = AgentResponse(content='{"changes": ' + str(code_changes) + '}')
        self.founder_ai_mock.get_response.return_value = founder_response
        self.developer_ai_mock.get_response.return_value = developer_response
        self.code_manager.apply_changes = MagicMock(return_value=True)

        result = self.orchestrator.run_improvement_cycle()

        self.assertTrue(result)
        self.founder_ai_mock.get_response.assert_called_once()
        self.developer_ai_mock.get_response.assert_called_once()
        self.code_manager.apply_changes.assert_called_once_with(code_changes)
        self.assertEqual(len(self.orchestrator.get_error_log()), 0)  # No errors expected
        self.assertGreater(len(self.orchestrator.get_agent_communication_log()), 0)
        self.assertFalse(mock_logger_error.called)


    @patch("src.orchestrator.logger.error")
    @patch("src.orchestrator.time.sleep", return_value=None)
    def test_run_improvement_cycle_founder_ai_failure_retries(self, mock_sleep, mock_logger_error):
        """Test retries when Founder AI fails."""
        self.founder_ai_mock.get_response.side_effect = Exception("API error")
        self.developer_ai_mock.get_response.return_value = AgentResponse(content='{"changes": []}')

        result = self.orchestrator.run_improvement_cycle()

        self.assertFalse(result)
        self.assertEqual(self.founder_ai_mock.get_response.call_count, 4)  # 3 retries + initial call
        self.assertTrue(mock_logger_error.called)
        self.assertGreater(len(self.orchestrator.get_error_log()), 0)


    @patch("src.orchestrator.logger.error")
    def test_run_improvement_cycle_developer_ai_failure(self, mock_logger_error):
        """Test handling of Developer AI failure."""
        self.founder_ai_mock.get_response.return_value = AgentResponse(content="Improve documentation")
        self.developer_ai_mock.get_response.side_effect = Exception("API error")

        result = self.orchestrator.run_improvement_cycle()

        self.assertFalse(result)
        self.assertTrue(mock_logger_error.called)
        self.assertGreater(len(self.orchestrator.get_error_log()), 0)

    @patch("src.orchestrator.logger.error")
    def test_run_improvement_cycle_safety_check_failure(self, mock_logger_error):
        """Test handling of Safety Check failure."""
        task = "Add a malicious script."
        code_changes = [{"file_path": "malicious.py", "content": "import os; os.system('rm -rf /') "}]

        founder_response = AgentResponse(content=task)
        developer_response = AgentResponse(content='{"changes": ' + str(code_changes) + '}')

        self.founder_ai_mock.get_response.return_value = founder_response
        self.developer_ai_mock.get_response.return_value = developer_response
        self.safety_checker.is_safe = MagicMock(return_value=False)

        result = self.orchestrator.run_improvement_cycle()

        self.assertFalse(result)
        self.safety_checker.is_safe.assert_called_once_with(code_changes)
        self.assertFalse(self.code_manager.apply_changes.called)
        self.assertTrue(mock_logger_error.called)
        self.assertGreater(len(self.orchestrator.get_error_log()), 0)


    @patch("src.orchestrator.logger.error")
    def test_run_improvement_cycle_apply_changes_failure(self, mock_logger_error):
        """Test handling of apply_changes failure."""
        task = "Update a file"
        code_changes = [{"file_path": "test.txt", "content": "new content"}]
        founder_response = AgentResponse(content=task)
        developer_response = AgentResponse(content='{"changes": ' + str(code_changes) + '}')

        self.founder_ai_mock.get_response.return_value = founder_response
        self.developer_ai_mock.get_response.return_value = developer_response
        self.code_manager.apply_changes = MagicMock(return_value=False)

        result = self.orchestrator.run_improvement_cycle()

        self.assertFalse(result)
        self.code_manager.apply_changes.assert_called_once_with(code_changes)
        self.assertTrue(mock_logger_error.called)
        self.assertGreater(len(self.orchestrator.get_error_log()), 0)

    def test_log_agent_interaction(self):
        """Test that agent interaction is logged correctly."""
        agent_name = "TestAgent"
        prompt = "Test prompt"
        response = "Test response"

        self.orchestrator._log_agent_interaction(agent_name, prompt, response)

        self.assertEqual(len(self.orchestrator.get_agent_communication_log()), 1)
        log_entry = self.orchestrator.get_agent_communication_log()[0]
        self.assertEqual(log_entry["agent_name"], agent_name)
        self.assertEqual(log_entry["prompt"], prompt)
        self.assertEqual(log_entry["response"], response)
```

```python
# tests/test_safety_checker.py
import unittest
from unittest.mock import MagicMock

from src.safety_checker import SafetyChecker
from src.config import Config

class TestSafetyChecker(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.safety_checker = SafetyChecker(self.config)

    def test_is_safe_all_safe(self):
        """Test is_safe with safe changes."""
        changes = [
            {"file_path": "src/example.py", "content": "def add(x, y):\n    return x + y"},
            {"file_path": "README.md", "content": "# My Project"},
        ]
        self.assertTrue(self.safety_checker.is_safe(changes))

    def test_is_safe_protected_file(self):
        """Test is_safe with modification of a protected file."""
        changes = [{"file_path": "src/config.py", "content": "..."}]
        self.assertFalse(self.safety_checker.is_safe(changes))

    def test_is_safe_protected_pattern(self):
        """Test is_safe with a disallowed pattern."""
        changes = [{"file_path": "src/example.py", "content": "import os; os.system('rm -rf /') "}]
        self.assertFalse(self.safety_checker.is_safe(changes))

    def test_is_safe_empty_content(self):
        """Test is_safe with empty content."""
        changes = [{"file_path": "src/example.py", "content": ""}]
        self.assertTrue(self.safety_checker.is_safe(changes))

    def test_is_safe_allow_all_file_changes_true(self):
        """Test is_safe with allow_all_file_changes set to true"""
        self.config.allow_all_file_changes = True
        changes = [{"file_path": "some_other_file.py", "content": "..."}]
        self.assertTrue(self.safety_checker.is_safe(changes))

    def test_is_safe_allow_all_file_changes_false_and_not_ai_maintained(self):
        """Test is_safe with allow_all_file_changes set to false and a file not maintained by AI"""
        self.config.allow_all_file_changes = False
        changes = [{"file_path": "some_other_file.py", "content": "..."}]
        self.assertFalse(self.safety_checker.is_safe(changes))

    def test_is_safe_allow_all_file_changes_false_and_ai_maintained(self):
        """Test is_safe with allow_all_file_changes set to false and a file maintained by AI"""
        self.config.allow_all_file_changes = False
        self.config.ai_maintained_files = ["some_other_file.py"]
        changes = [{"file_path": "some_other_file.py", "content": "..."}]
        self.assertTrue(self.safety_checker.is_safe(changes))
```

```python
# tests/test_code_reader.py
import unittest
from unittest.mock import MagicMock, patch

from src.agents.code_reader import CodeReader
from src.config import Config
from src.agents.agent import Agent, AgentResponse

class TestCodeReader(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.mock_agent = MagicMock(spec=Agent)
        self.code_reader = CodeReader(self.config, self.mock_agent)

    def test_summarize_code_success(self):
        """Test successful code summarization."""
        file_path = "test_file.py"
        code = "def my_function():\n  pass"
        summary = "This function does nothing."
        self.mock_agent.get_response.return_value = AgentResponse(content=summary)
        with patch("builtins.open", unittest.mock.mock_open(read_data=code)) as mock_file:
            result = self.code_reader.summarize_code(file_path)
            mock_file.assert_called_once_with(file_path, "r")
            self.assertEqual(result, summary)
            self.mock_agent.get_response.assert_called_once()

    def test_summarize_code_file_not_found(self):
        """Test handling of FileNotFoundError."""
        file_path = "nonexistent_file.py"
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = self.code_reader.summarize_code(file_path)
            self.assertEqual(result, "File not found.")
            self.mock_agent.get_response.assert_not_called()

    def test_summarize_code_agent_failure(self):
        """Test handling of Agent failure."""
        file_path = "test_file.py"
        code = "def my_function():\n  pass"
        self.mock_agent.get_response.side_effect = Exception("API error")

        with patch("builtins.open", unittest.mock.mock_open(read_data=code)):
            result = self.code_reader.summarize_code(file_path)

        self.assertEqual(result, "Error summarizing code.")
        self.mock_agent.get_response.assert_called_once()

    def test_summarize_code_caching(self):
        """Test that the cache is used."""
        file_path = "test_file.py"
        code = "def my_function():\n  pass"
        summary = "This function does nothing."
        self.mock_agent.get_response.return_value = AgentResponse(content=summary)

        with patch("builtins.open", unittest.mock.mock_open(read_data=code)):
            # First call - should go to the agent
            self.code_reader.summarize_code(file_path)
            self.mock_agent.get_response.assert_called_once()

            # Reset the mock and call again - should use cache
            self.mock_agent.get_response.reset_mock()
            self.code_reader.summarize_code(file_path)
            self.mock_agent.get_response.assert_not_called()

    def test_summarize_code_empty_file(self):
        """Test handling of empty file"""
        file_path = "test_file.py"
        code = ""
        with patch("builtins.open", unittest.mock.mock_open(read_data=code)) as mock_file:
            result = self.code_reader.summarize_code(file_path)
            mock_file.assert_called_once_with(file_path, "r")
            self.assertEqual(result, "File is empty.")
            self.mock_agent.get_response.assert_not_called()
```

```python
# tests/test_code_manager.py
import unittest
from unittest.mock import patch

from src.code_manager import CodeManager

class TestCodeManager(unittest.TestCase):
    def setUp(self):
        self.repo_path = "./test_repo"
        self.code_manager = CodeManager(self.repo_path)
        # Ensure the test directory exists
        import os
        if not os.path.exists(self.repo_path):
            os.makedirs(self.repo_path)

    def tearDown(self):
        # Clean up the test directory after each test
        import shutil
        import os
        if os.path.exists(self.repo_path):
            shutil.rmtree(self.repo_path)

    def test_apply_changes_success(self):
        """Test successful application of code changes."""
        changes = [
            {"file_path": "test_file.py", "content": "def test_function():\n    pass"},
            {"file_path": "src/utils.py", "content": "def helper():\n    return True"},
        ]

        result = self.code_manager.apply_changes(changes)

        self.assertTrue(result)
        # Verify the files were created with the correct content
        import os
        self.assertTrue(os.path.exists(os.path.join(self.repo_path, "test_file.py")))
        self.assertTrue(os.path.exists(os.path.join(self.repo_path, "src/utils.py")))
        with open(os.path.join(self.repo_path, "test_file.py"), "r") as f:
            self.assertEqual(f.read(), "def test_function():\n    pass")
        with open(os.path.join(self.repo_path, "src/utils.py"), "r") as f:
            self.assertEqual(f.read(), "def helper():\n    return True")

    def test_apply_changes_failure(self):
        """Test failure during application of changes (e.g., due to permission issues)."""
        # Simulate a failure by providing an invalid file path
        changes = [{"file_path": "/invalid/path/test_file.py", "content": "..."}]
        result = self.code_manager.apply_changes(changes)
        self.assertFalse(result)

    def test_apply_changes_missing_file_path(self):
        """Test handling of missing file path in changes."""
        changes = [{"content": "..."}]  # Missing file_path
        result = self.code_manager.apply_changes(changes)
        self.assertTrue(result) #Should not fail but skip the change.

    def test_apply_changes_missing_content(self):
        """Test handling of missing content in changes."""
        changes = [{"file_path": "test_file.py"}]  # Missing content
        result = self.code_manager.apply_changes(changes)
        self.assertTrue(result)  #Should not fail but skip the change.

    def test_create_merge_request(self):
        """Test the create_merge_request function."""
        branch_name = "feature/test-branch"
        title = "Test Merge Request"
        description = "This is a test merge request."

        result = self.code_manager.create_merge_request(branch_name, title, description)

        self.assertTrue(result)  # Assert the function returns True (simulated success)
```
