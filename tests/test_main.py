```python
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app, Observability, CycleReport

class TestMain(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch('main.Observability.get_cycle_report')
    def test_get_cycle_report_success(self, mock_get_cycle_report):
        cycle_id = "cycle-123"
        report_data = CycleReport(
            cycle_id=cycle_id,
            log_messages=["Log message 1", "Log message 2"],
            summaries=["Summary 1", "Summary 2"],
            pull_request_links=["link1", "link2"]
        )
        mock_get_cycle_report.return_value = report_data

        response = self.client.get(f"/cycles/{cycle_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["cycle_id"], cycle_id)
        self.assertEqual(data["log_messages"], ["Log message 1", "Log message 2"])
        self.assertEqual(data["summaries"], ["Summary 1", "Summary 2"])
        self.assertEqual(data["pull_request_links"], ["link1", "link2"])
        mock_get_cycle_report.assert_called_once_with(cycle_id)

    @patch('main.Observability.get_cycle_report')
    def test_get_cycle_report_not_found(self, mock_get_cycle_report):
        cycle_id = "cycle-404"
        mock_get_cycle_report.return_value = None

        response = self.client.get(f"/cycles/{cycle_id}")
        self.assertEqual(response.status_code, 404)
        mock_get_cycle_report.assert_called_once_with(cycle_id)

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Hello, World!"})
```