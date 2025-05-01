import logging
import ast
import re
from typing import Dict, Any, List, Tuple
import os

class SafetyChecker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Protected files are core system files that should never be modified
        # These files contain critical functionality that keeps the system running
        # Modifying these could break the self-improvement mechanism itself
        self.protected_files = [
            'src/safety_checker.py',  # Contains safety checks - modifying this could bypass all safety
            'src/code_manager.py',    # Handles version control and backups - critical for system stability
            'src/config.py',           # Contains system configuration - modifying could break the entire system
            'src/observability.py',    # Added observability module to protected files
            'src/rate_limits.py'       # Contains rate limiting configuration - critical for API stability
        ]
        
        # Special files that can be modified by the AI agents
        self.ai_maintained_files = [
            'README_ai.md'  # File maintained by the AI agents
        ]
        
        # Protected patterns are critical code patterns that should never be changed
        # These patterns represent core functionality that must be preserved
        self.protected_patterns = [
            r'async def _create_backup',    # Backup functionality must be preserved for system safety
            r'async def _restore_backup',   # Restore functionality must be preserved for system safety
            r'class SafetyChecker',         # Safety checker class must not be modified
            r'class CodeManager',           # Code manager class must not be modified
            r'class Settings',               # Settings class must not be modified
            r'class Observability:',         # Added observability class pattern
            r'class RateLimiter:',           # Added rate limiter class pattern
            r'def _create_backup\(self\):',  # Added backup method pattern
            r'def _restore_backup\(self\):',  # Added restore method pattern
            r'def validate_plan\(self\):',     # Added validate_plan method pattern
            r'def test_changes\(self\):',       # Added test_changes method pattern
            r'def create_pull_request\(self\):', # Added create_pull_request method pattern
            r'def get_cycle_summary\(self\):',    # Added get_cycle_summary method pattern
            r'def check_openai_limit\(self\):',   # Added rate limiting method pattern
            r'def check_github_limit\(self\):'    # Added rate limiting method pattern
        ]
    
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
                if file_path.endswith('.py'):
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
                        issues.append(f"Changes attempt to modify protected pattern: {pattern}")
            
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
            'os.system',    # Could execute arbitrary system commands
            'subprocess',   # Could spawn arbitrary processes
            'eval',         # Could execute arbitrary code
            'exec'          # Could execute arbitrary code
        ]
        for imp in dangerous_imports:
            if imp in content:
                issues.append(f"Dangerous import/function found in {file_path}: {imp}")
        
        # Check for dangerous file system operations that could damage the system
        dangerous_fs_ops = [
            'shutil.rmtree',  # Could delete entire directories
            'os.remove',      # Could delete files
            'os.rename'       # Could move or rename files
        ]
        for op in dangerous_fs_ops:
            if op in content:
                issues.append(f"Dangerous file system operation found in {file_path}: {op}")
        
        return issues 