"""
Tests for the RepoReader class.
"""

import pytest
from src.repo_reader import RepoReader
from src.config import settings

@pytest.fixture
def repo_reader():
    """Fixture to create a RepoReader instance."""
    return RepoReader(settings.repo_url)

def test_init(repo_reader):
    """Test RepoReader initialization."""
    assert repo_reader.repo_url == settings.repo_url
    assert repo_reader.branch == settings.branch
    assert repo_reader.owner == "wenhongg"
    assert repo_reader.repo_name == "ai-startup"

def test_get_file_content(repo_reader):
    """Test getting file content."""
    # Test with a real file
    content = repo_reader.get_file_content("README.md")
    assert content is not None
    assert "ai-startup" in content
    
    # Test with a non-existent file
    content = repo_reader.get_file_content("nonexistent.py")
    assert content is None

def test_get_python_files(repo_reader):
    """Test getting Python files from repository."""
    files = repo_reader.get_python_files()
    assert len(files) > 0
    assert all(file["path"].endswith(".py") for file in files)
    assert all("content" in file for file in files)

def test_get_file_history(repo_reader):
    """Test getting file commit history."""
    history = repo_reader.get_file_history("README.md")
    assert len(history) > 0
    assert all("sha" in commit for commit in history)
    assert all("message" in commit for commit in history)
    assert all("date" in commit for commit in history)
    
    # Test with limit
    history = repo_reader.get_file_history("README.md", limit=1)
    assert len(history) == 1

def test_get_all_files(repo_reader):
    """Test getting all files from repository."""
    # Test getting files from root directory
    files = repo_reader.get_all_files()
    assert len(files) > 0
    assert "README.md" in files
    assert any(file.endswith(".py") for file in files)
    
    # Test getting files from a specific directory
    src_files = repo_reader.get_all_files("src")
    assert len(src_files) > 0
    assert all(file.startswith("src/") for file in src_files)
    assert any(file.endswith(".py") for file in src_files)
    
    # Test with non-existent directory
    files = repo_reader.get_all_files("nonexistent")
    assert len(files) == 0 