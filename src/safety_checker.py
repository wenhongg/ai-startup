```python
import logging
import ast
import re
from typing import Dict, Any, List, Tuple
import os
from src.config import (
    PROTECTED_FILES,
    AI_MAINTAINED_FILES,
    PROTECTED_PATTERNS,
)


class SafetyChecker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Protected files are core system files that should never be modified
        # These files contain critical functionality that keeps the system running
        # Modifying these could break the self-improvement mechanism itself
        self.protected_files = PROTECTED_FILES

        # Special files that can be modified by the AI agents
        self.ai_maintained_files = AI_MAINTAINED_FILES

        # Protected patterns are critical code patterns that should never be changed
        # These patterns represent core functionality that must be preserved
        self.protected_patterns = PROTECTED_PATTERNS

    async def validate_plan(self, plan: str) -> Tuple[bool, List[str]]:
        """
        Validate the implementation plan for safety
        Returns a tuple of (is_valid, issues)

        Checks:
        1. Protected Files: Ensures the plan doesn't attempt to modify core system files
        2. Protected Patterns: Ensures the plan doesn't attempt to modify critical code patterns
        """
        issues = []
        try:
            # Check for protected file modifications
            for file in self.protected_files:
                if file in plan:
                    issues.append(f"Plan attempts to modify protected file: {file}")

            # Check for protected pattern modifications
            for pattern in self.protected_patterns:
                if re.search(pattern, plan):
                    issues.append(f"Plan attempts to modify protected pattern: {pattern}")

            return len(issues) == 0, issues

        except Exception as e:
            self.logger.error(f"Error validating plan: {str(e)}")
            issues.append(f"Error during validation: {str(e)}")
            return False, issues

    async def test_changes(self, changes: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Test the proposed changes for safety and functionality
        Returns a tuple of (is_valid, issues)

        Checks:
        1. Syntax: Ensures all Python files have valid syntax
        2. Protected Files: Ensures no core system files are modified
        3. Protected Patterns: Ensures no critical code patterns are modified
        4. Safety: Checks for dangerous operations in the code
        """
        issues = []
        try:
            # Check each file for syntax errors
            for file_path, content in changes.items():
                if file_path.endswith(".py"):
                    try:
                        ast.parse(content)
                    except SyntaxError as e:
                        issues.append(f"Syntax error in {file_path}: {str(e)}")

            # Check for protected file modifications
            for file in self.protected_files:
                if file in changes:
                    issues.append(f"Changes attempt to modify protected file: {file}")

            # Check for protected pattern modifications
            for pattern in self.protected_patterns:
                for content in changes.values():
                    if re.search(pattern, content):
                        issues.append(
                            f"Changes attempt to modify protected pattern: {pattern}"
                        )

            # Check for safety issues in each file
            for file_path, content in changes.items():
                # Skip safety checks for AI-maintained files
                if file_path in self.ai_maintained_files:
                    continue
                file_issues = self._check_file_safety(file_path, content)
                issues.extend(file_issues)

            return len(issues) == 0, issues

        except Exception as e:
            self.logger.error(f"Error testing changes: {str(e)}")
            issues.append(f"Error during testing: {str(e)}")
            return False, issues

    def _check_file_safety(self, file_path: str, content: str) -> List[str]:
        """
        Check a single file for safety issues
        Returns a list of safety issues found

        Checks for:
        1. Dangerous Imports: Functions that could be used maliciously
        2. File System Operations: Operations that could damage the system
        """
        issues = []

        # Check for dangerous imports that could be used maliciously
        dangerous_imports = [
            "os.system",  # Could execute arbitrary system commands
            "subprocess.run",  # Could spawn arbitrary processes
            "subprocess.Popen",  # Could spawn arbitrary processes
            "eval",  # Could execute arbitrary code
            "exec",  # Could execute arbitrary code
            "pickle.load",  # Could execute arbitrary code
            "marshal.load", # Could execute arbitrary code
        ]
        for imp in dangerous_imports:
            if imp in content:
                issues.append(f"Dangerous import/function found in {file_path}: {imp}")

        # Check for dangerous file system operations that could damage the system
        dangerous_fs_ops = [
            "shutil.rmtree",  # Could delete entire directories
            "os.remove",  # Could delete files
            "os.rename",  # Could move or rename files
            "os.replace",  # Could replace files
            "open(file, 'w'", # Could overwrite files
            "open(file, 'wb'", # Could overwrite files
            "open(file, 'a'", # Could append to files
        ]
        for op in dangerous_fs_ops:
            if op in content:
                issues.append(f"Dangerous file system operation found in {file_path}: {op}")

        # Additional checks for file operations and paths
        if "open(" in content:
            for match in re.finditer(r"open\((.*)\)", content):
                try:
                    args_str = match.group(1)
                    args = [s.strip().strip("'").strip('"') for s in args_str.split(",") if s.strip()]
                    if len(args) > 0:
                        file_path_arg = args[0]
                        # Basic check: prevent hardcoded absolute paths
                        if os.path.isabs(file_path_arg):
                            issues.append(f"Absolute path used in open() call: {file_path_arg}")
                except Exception as e:
                    self.logger.warning(f"Error parsing open() arguments: {e}")

        # Check for command execution with user-provided input (e.g., subprocess)
        if "subprocess.run" in content or "subprocess.Popen" in content:
            for match in re.finditer(r"(subprocess\.run|subprocess\.Popen)\((.*?)\)", content):
                try:
                    args_str = match.group(2)
                    args = [s.strip().strip("'").strip('"') for s in args_str.split(",") if s.strip()]
                    for arg in args:
                        if arg.startswith("f") or arg.startswith("%"):
                            issues.append(f"Potential command injection vulnerability in {file_path}: {match.group(0)}")

                except Exception as e:
                     self.logger.warning(f"Error parsing subprocess arguments: {e}")


        return issues
```

## Technical Analysis of Requirements

The pull request requests several enhancements across the system, focusing on robustness, security, and performance. Specifically:

*   **Orchestrator:** Improve error handling with `try-except` blocks, detailed logging including stack traces, and retry mechanisms with exponential backoff for agent interactions. Also includes logging of all communication.
*   **SafetyChecker:** Enhance security by expanding `protected_patterns`, moving configuration to `config.py`, and adding more granular file system and import checks.
*   **CodeReader:** Optimize performance by using `functools.lru_cache` for caching code summaries, improving the summary prompt, and improving error handling.
*   **CodeManager:** Adding functions to perform merge operations, including creating merge requests.
*   **Comprehensive Logging and Reporting:** Implement structured logging (JSON format) for all steps, including agents, prompts, responses, and resulting actions.
*   **Code Quality:** Integrate linters.

The primary changes relate to the `SafetyChecker`. This involves:
1.  Moving the configurations for `protected_files`, `ai_maintained_files`, and `protected_patterns` to `config.py`.
2.  Adding more granular safety checks within the `_check_file_safety` function:
    *   Preventing the use of dangerous imports, such as those related to arbitrary code execution and file system manipulation.
    *   Preventing dangerous file system operations like deletion and renaming.
    *   Checking for potentially malicious file paths used with `open()`.
    *   Checking for command injection vulnerabilities in subprocess calls.

## Implementation Plan

1.  **Modify `SafetyChecker`:**
    *   Import `PROTECTED_FILES`, `AI_MAINTAINED_FILES`, and `PROTECTED_PATTERNS` from `src/config.py`.
    *   Implement the more granular safety checks in `_check_file_safety`. Specifically, add checks for dangerous imports, file system operations,  and potentially malicious file paths and subprocess calls.

2.  **Modify `src/config.py` (if not already present, create it)**
    ```python
    PROTECTED_FILES = [
        'src/safety_checker.py',
        'src/code_manager.py',
        'src/config.py',
        'src/observability.py',
        'src/rate_limits.py'
    ]
    AI_MAINTAINED_FILES = [
        'README_ai.md'
    ]
    PROTECTED_PATTERNS = [
        r'async def _create_backup',
        r'async def _restore_backup',
        r'class SafetyChecker',
        r'class CodeManager',
        r'class Settings',
        r'class Observability:',
        r'class RateLimiter:',
        r'def _create_backup\(self\):',
        r'def _restore_backup\(self\):',
        r'def validate_plan\(self\):',
        r'def test_changes\(self\):',
        r'def create_pull_request\(self\):',
        r'def get_cycle_summary\(self\):',
        r'def check_openai_limit\(self\):',
        r'def check_github_limit\(self\):'
    ]
    ```

3.  **Address other requirements:** This includes the other areas, but this change impacts the code most significantly. These will be handled in separate commits/PRs.

## Safety Considerations

*   **Configuration:** Incorrect configuration in `config.py` can lead to security vulnerabilities (e.g., allowing modification of protected files) or hinder development. The changes move the configuration into a dedicated file.
*   **Overly Restrictive Checks:** The new safety checks must be carefully implemented. Overly restrictive checks could block legitimate code modifications. The tests will help to address this.
*   **Error Handling:** Robust error handling is included to prevent unexpected behavior and to provide informative logging.

## Testing Approach

1.  **Unit Tests for `SafetyChecker`:**
    *   **Test Protected Files:** Ensure that attempts to modify files listed in `PROTECTED_FILES` are correctly identified and blocked.
    *   **Test Protected Patterns:** Ensure that attempts to modify code patterns matching entries in `PROTECTED_PATTERNS` are correctly identified and blocked.
    *   **Test Dangerous Imports:** Test that the `_check_file_safety` function correctly identifies and flags the use of dangerous imports.
    *   **Test Dangerous File System Operations:** Test that the `_check_file_safety` function correctly identifies and flags the use of dangerous file system operations.
    *   **Test File Path Checks:** Tests to ensure that the new file path checks correctly identify and flag potential issues.
    *   **Test Subprocess Checks:** Test to ensure that the new subprocess checks correctly identify and flag potential issues.
    *   **Test AI Maintained Files:** Test to ensure that `ai_maintained_files` are skipped by the safety checks.
2.  **Manual Testing:** Manually review the changes and run the system to verify that the safety checks function as intended and that the system remains operational.
3.  **Integration Tests:** Verify that the safety checks work correctly in the context of the entire system, testing the interaction of the orchestrator and agents.

## Rollback Plan

1.  **Version Control:** Since the changes are committed with version control, it is easy to revert to the previous state.
2.  **Backup:** Ensure that a backup of the current state is made before deploying the changes.
3.  **Revert Changes:** In case of issues, revert the changes in the pull request.
4.  **Hotfix:** If a critical security vulnerability is introduced, a hotfix can be implemented to disable or modify the failing safety checks.
