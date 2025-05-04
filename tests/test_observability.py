import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app  # Assuming your FastAPI app is defined in main.py
from src.observability import Observability

class TestObservability(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.observability = Observability()

    def test_status_endpoint_returns_200(self):
        response = self.client.get("/status")
        self.assertEqual(response.status_code, 200)

    def test_status_endpoint_returns_json(self):
        response = self.client.get("/status")
        self.assertEqual(response.headers["content-type"], "application/json")

    def test_status_endpoint_initial_state(self):
        response = self.client.get("/status")
        data = response.json()
        self.assertIn("cycle_data", data)
        self.assertEqual(data["cycle_data"], {})

    @patch('src.observability.logging.info')
    def test_start_stage_updates_cycle_data(self, mock_log):
        proposal_title = "Test Proposal"
        proposal_description = "Test Description"
        pr_url = "https://example.com/pr"
        self.observability.start_stage("test_stage", proposal_title, proposal_description, pr_url)
        response = self.client.get("/status")
        data = response.json()
        self.assertIn("cycle_data", data)
        self.assertIn("test_stage", data["cycle_data"])
        stage_data = data["cycle_data"]["test_stage"]
        self.assertIn("start_time", stage_data)
        self.assertIn("proposal_title", stage_data)
        self.assertIn("proposal_description", stage_data)
        self.assertIn("pr_url", stage_data)
        self.assertEqual(stage_data["proposal_title"], proposal_title)
        self.assertEqual(stage_data["proposal_description"], proposal_description)
        self.assertEqual(stage_data["pr_url"], pr_url)
        mock_log.assert_called()

    @patch('src.observability.logging.info')
    def test_end_stage_updates_cycle_data(self, mock_log):
        stage_name = "test_stage"
        self.observability.start_stage(stage_name, "title", "desc", "url")
        self.observability.end_stage(stage_name)
        response = self.client.get("/status")
        data = response.json()
        self.assertIn("cycle_data", data)
        self.assertIn(stage_name, data["cycle_data"])
        stage_data = data["cycle_data"][stage_name]
        self.assertIn("end_time", stage_data)
        mock_log.assert_called()

    @patch('src.observability.logging.error')
    def test_error_updates_cycle_data(self, mock_log):
        stage_name = "test_stage"
        error_message = "Test Error"
        self.observability.start_stage(stage_name, "title", "desc", "url")
        self.observability.log_error(stage_name, error_message)
        response = self.client.get("/status")
        data = response.json()
        self.assertIn("cycle_data", data)
        self.assertIn(stage_name, data["cycle_data"])
        stage_data = data["cycle_data"][stage_name]
        self.assertIn("error", stage_data)
        self.assertEqual(stage_data["error"], error_message)
        mock_log.assert_called()

    def test_status_endpoint_with_multiple_stages(self):
        self.observability.start_stage("stage1", "title1", "desc1", "url1")
        self.observability.end_stage("stage1")
        self.observability.start_stage("stage2", "title2", "desc2", "url2")
        response = self.client.get("/status")
        data = response.json()
        self.assertIn("cycle_data", data)
        self.assertIn("stage1", data["cycle_data"])
        self.assertIn("stage2", data["cycle_data"])
        self.assertIn("end_time", data["cycle_data"]["stage1"])
        self.assertIn("start_time", data["cycle_data"]["stage2"])

    def test_status_endpoint_sensitive_data_redaction(self):
        # Assuming that 'secrets' is sensitive and should be redacted
        # This part needs adaptation depending on how you manage and store sensitive information.
        stage_name = "secrets_stage"
        sensitive_info = "This is a secret"  # example, change it to whatever you consider secret
        self.observability.start_stage(stage_name, "title", "desc", "url")

        # Simulate storing the secret information within the cycle_data (adapt based on implementation)
        self.observability.cycle_data[stage_name]["sensitive_info"] = sensitive_info
        response = self.client.get("/status")
        data = response.json()
        self.assertIn("cycle_data", data)
        self.assertIn(stage_name, data["cycle_data"])
        self.assertNotIn("sensitive_info", data["cycle_data"][stage_name]) # check is redacted
        # If we are storing the secret in a custom field. adapt this line.
        # self.assertEqual(data["cycle_data"][stage_name]["sensitive_info"], "REDACTED") # or whatever you replace it with

    def test_status_endpoint_error_handling_no_proposal(self):
        # Tests the case where proposal details are not provided when start_stage is called
        stage_name = "no_proposal_stage"
        self.observability.start_stage(stage_name, None, None, None) # Simulate no details provided.
        response = self.client.get("/status")
        data = response.json()
        self.assertIn("cycle_data", data)
        self.assertIn(stage_name, data["cycle_data"])
        stage_data = data["cycle_data"][stage_name]
        self.assertIsNone(stage_data.get("proposal_title"))
        self.assertIsNone(stage_data.get("proposal_description"))
        self.assertIsNone(stage_data.get("pr_url"))