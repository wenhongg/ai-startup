"""
Tests for the CodeManager class.
"""

import pytest
from src.code_manager import CodeManager
from src.config import settings
import os

@pytest.fixture
def code_manager():
    """Fixture to create a CodeManager instance."""
    return CodeManager()

def test_create_pull_request(code_manager):
    """Test creating a pull request with a new file."""
    # Test data
    test_content = """# Test File
    
This is a test file created by the test suite.
It should be added to the repository via a pull request.
"""
    changes = {
        "test.md": test_content
    }
    title = "Test: Add test.md file"
    description = "This is a test pull request that adds a test markdown file."
    
    # Create pull request
    pr_url = code_manager.create_pull_request(changes, title, description)
    
    # Verify the pull request was created
    assert pr_url is not None
    assert "github.com" in pr_url
    assert "pull" in pr_url
    
    # Clean up - delete the test file
    try:
        # Get the file content to get its SHA
        file_content = code_manager.repo.get_contents("test.md", ref=settings.branch)
        code_manager.repo.delete_file(
            "test.md",
            "Clean up test file",
            file_content.sha,
            branch=settings.branch
        )
    except Exception as e:
        print(f"Warning: Could not clean up test file: {e}") 