```python
"""
System orchestrator that coordinates the improvement cycle.
"""

import logging
import json
import time
import traceback
from typing import Dict, Any, List
from functools import wraps
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .rate_limits import RateLimiter
from .code_manager import CodeManager
from .agents.founder import FounderAI
from .agents.developer import DeveloperAI
from .agents.code_reader import CodeReader
from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_agent_interaction(func):
    """Decorator to log agent interactions (prompts and responses)."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]  # Assuming the first argument is 'self'
        agent_name = func.__qualname__.split('.')[1].replace('_generate', '').replace('_implement', '') # Extract agent name
        try:
            prompt = kwargs.get('prompt', None)  # Get prompt if it exists, otherwise None
            if prompt:
                logger.info(json.dumps({
                    "agent": agent_name,
                    "interaction_type": "prompt",
                    "prompt": prompt
                }))
            result = func(*args, **kwargs)
            logger.info(json.dumps({
                "agent": agent_name,
                "interaction_type": "response",
                "response": str(result)  # Log the string representation of the result
            }))
            return result
        except Exception as e:
            logger.error(json.dumps({
                "agent": agent_name,
                "interaction_type": "error",
                "error_message": str(e),
                "traceback": traceback.format_exc()
            }))
            raise
    return wrapper


class SystemOrchestrator:
    """Coordinates the improvement cycle between AI agents."""
    
    def __init__(self):
        """Initialize the orchestrator with all necessary components."""
        self.rate_limiter = RateLimiter()
        self.code_manager = CodeManager()
        self.code_reader = CodeReader()
        self.founder = FounderAI(self.code_reader)
        self.developer = DeveloperAI(self.code_reader)
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10),
           retry=retry_if_exception_type(Exception))  # Retry for any exception
    @log_agent_interaction
    def _run_founder_interaction(self, product_summaries: Dict[str, str]) -> str:
        """Handles the interaction with the FounderAI, including retries and error handling."""
        try:
            return self.founder.generate_proposal(product_summaries)
        except Exception as e:
            logger.error(f"FounderAI interaction failed: {e}\n{traceback.format_exc()}")
            raise  # Re-raise the exception to trigger retry


    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10),
           retry=retry_if_exception_type(Exception))  # Retry for any exception
    @log_agent_interaction
    def _run_developer_interaction(self, proposal: str) ->  tuple[Dict[str, str], str, str]:
        """Handles the interaction with the DeveloperAI, including retries and error handling."""
        try:
            return self.developer.implement_changes(proposal)
        except Exception as e:
            logger.error(f"DeveloperAI interaction failed: {e}\n{traceback.format_exc()}")
            raise # Re-raise the exception to trigger retry

    def run_improvement_cycle(self):
        """Run a complete improvement cycle."""
        logger.info("Starting improvement cycle...")
        try:
            # Summarize the repository first
            logger.info("Summarizing repository...")
            self.code_reader.summarize_repository()

            # Get product summaries and generate proposal
            logger.info("Generating proposal...")
            product_summaries = self.code_reader.get_code_summaries()
            proposal = self._run_founder_interaction(product_summaries)

            logger.info("Implementing changes...")
            # Developer reviews and implements
            changes, title, description = self._run_developer_interaction(proposal)

            logger.info(f"Changes: {changes}")
            logger.info(f"Title: {title}")
            logger.info(f"Description: {description}")

            logger.info("Creating pull request...")
            # Create pull request with changes
            pr_url = self.code_manager.create_pull_request(changes, title, description)
            logger.info(f"Created pull request: {pr_url}")

        except Exception as e:
            logger.error(f"Critical error in improvement cycle: {e}\n{traceback.format_exc()}")
            # Consider additional error handling/alerting here (e.g., send notification)
            raise # Re-raise to allow the calling function to handle it if necessary
        logger.info("Improvement cycle completed.")

```

**Technical Analysis of Requirements:**

The pull request details require several key changes:

1.  **Orchestrator Enhancement:**
    *   Implement `try-except` blocks in `run_improvement_cycle` to catch exceptions.
    *   Log errors with stack traces.
    *   Implement a retry mechanism with exponential backoff for AI agent interactions.
    *   Log all communication between the `Orchestrator` and AI agents (prompts and responses).
2.  **SafetyChecker Enhancement:** (This part will be handled in a separate file, not in this response.)
3.  **CodeReader Optimization:** (This part will be handled in a separate file, not in this response.)
4.  **CodeManager enhancement:** (This part will be handled in a separate file, not in this response.)
5.  **Comprehensive Logging and Reporting:** Implement structured logging (JSON formatted) for all steps, including agents, prompts, responses, and actions.
6.  **Code Quality:** Integrate linters (Black, isort, flake8, mypy) into the development process (handled separately via pre-commit).

**Implementation Plan:**

1.  **Modify `run_improvement_cycle`:** Wrap the main logic of `run_improvement_cycle` in a `try-except` block. Log any caught exceptions with stack traces using the `logging` module.
2.  **Implement Retry Mechanism:** Use the `tenacity` library to implement retries with exponential backoff for calls to AI agents.
3.  **Implement Logging of Agent Interactions:** Create a decorator `log_agent_interaction` to log the prompts and responses between the `Orchestrator` and AI agents. The decorator will log the agent name, interaction type (prompt/response/error), the prompt/response content, and the stack trace for errors.
4.  **Use Structured Logging:** Utilize JSON formatting for the log messages to enable easier parsing and analysis of the logs.
5.  **Add Logging Statements:** Add logging statements at the start and end of the `run_improvement_cycle` function and at various stages within the function to provide visibility into the progress and outcome of each step.

**Safety Considerations:**

1.  **Error Handling:** The `try-except` blocks and retry mechanism will increase the robustness of the system by gracefully handling errors and attempting to recover from transient issues.
2.  **Logging:** Comprehensive logging with stack traces and structured JSON formatting will aid in debugging and understanding the system's behavior. However, increased logging volume should be considered and monitored to prevent excessive storage consumption.
3.  **Retry Mechanism:** The retry mechanism with exponential backoff prevents the system from failing immediately due to temporary API issues. However, overly aggressive retries could potentially increase API usage costs.
4.  **Configuration:** Ensure proper setup for logging, e.g., log level and handler, to avoid a flood of logs or missing crucial information.

**Testing Approach:**

1.  **Unit Tests for `SystemOrchestrator`:**
    *   **Error Handling:** Write tests that simulate exceptions being raised by the AI agents and verify that the `try-except` blocks in `run_improvement_cycle` catch these exceptions and that the error messages and stack traces are logged correctly.
    *   **Retry Mechanism:** Tests should verify that the retry mechanism is triggered upon exceptions and that it attempts to retry a specified number of times with an exponential backoff strategy.  Use mocking to simulate AI agent interactions and control the exceptions.
    *   **Logging:** Tests should verify that agent interactions (prompts and responses) are correctly logged in the expected format (JSON) and that the logging includes all necessary information (agent name, interaction type, prompt/response content). Use a `StringIO` or similar to capture the logs for testing.
2.  **Integration Tests (Optional):** Integration tests might be useful to test the interaction between the `Orchestrator`, `CodeManager`, and AI agents.

**Rollback Plan:**

1.  **Version Control:** Since all changes are committed to version control (e.g., Git), rolling back to a previous version is straightforward.
2.  **Backup:** Before making significant changes, especially those affecting core system functionality (such as the `run_improvement_cycle`), create a backup of the code.
3.  **Revert Changes:** If the changes introduce issues, revert the specific commits related to these changes.
4.  **Disable New Features:** If necessary, temporarily disable the newly introduced features (e.g., the retry mechanism or agent interaction logging) by commenting out or removing relevant code, or through a configuration setting.
5.  **Monitor Logs:** After deployment, closely monitor the logs for any errors or unexpected behavior.
