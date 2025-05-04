from fastapi.testclient import TestClient
from main import app
import logging
from unittest.mock import patch

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

@patch('main.Observability.get_cycle_data')
def test_status_endpoint(mock_get_cycle_data):
    mock_get_cycle_data.return_value = {
        "stage": "proposal",
        "start_time": "2024-10-27T10:00:00",
        "end_time": "2024-10-27T10:15:00",
        "proposal_title": "Test Proposal",
        "proposal_description": "Test Description",
        "pr_url": "https://example.com/pr",
        "error": None
    }
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "stage" in data
    assert "start_time" in data
    assert "end_time" in data
    assert "proposal_title" in data
    assert "proposal_description" in data
    assert "pr_url" in data
    assert "error" in data

@patch('main.Observability.get_cycle_data')
def test_status_endpoint_with_error(mock_get_cycle_data):
    mock_get_cycle_data.return_value = {
        "stage": "code_generation",
        "start_time": "2024-10-27T10:15:00",
        "end_time": None,
        "proposal_title": "Test Proposal",
        "proposal_description": "Test Description",
        "pr_url": None,
        "error": "An error occurred"
    }
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "stage" in data
    assert "error" in data
    assert data["error"] == "An error occurred"

@patch('main.Observability.get_cycle_data')
def test_status_endpoint_no_data(mock_get_cycle_data):
    mock_get_cycle_data.return_value = {}
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "stage" in data
    assert data["stage"] is None
    assert "start_time" in data
    assert data["start_time"] is None
    assert "end_time" in data
    assert data["end_time"] is None
    assert "proposal_title" in data
    assert data["proposal_title"] is None
    assert "proposal_description" in data
    assert data["proposal_description"] is None
    assert "pr_url" in data
    assert data["pr_url"] is None
    assert "error" in data
    assert data["error"] is None