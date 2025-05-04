```python
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app, Observability
import json
import datetime

client = TestClient(app)

class TestMain(unittest.TestCase):

    def setUp(self):
        self.observability = Observability()
        self.test_cycle_data_running = {
            "cycle_id": "test_cycle_1",
            "start_time": datetime.datetime.now().isoformat(),
            "end_time": None,
            "status": "running",
            "phase": "analyzing",
            "details": {"step": 1, "total_steps": 3}
        }

        self.test_cycle_data_completed = {
            "cycle_id": "test_cycle_2",
            "start_time": datetime.datetime.now().isoformat(),
            "end_time": datetime.datetime.now().isoformat(),
            "status": "completed",
            "phase": None,
            "details": {"summary": "Changes implemented"}
        }
        self.test_cycle_data_failed = {
            "cycle_id": "test_cycle_3",
            "start_time": datetime.datetime.now().isoformat(),
            "end_time": datetime.datetime.now().isoformat(),
            "status": "failed",
            "phase": None,
            "details": {"error": "Failed to parse data"}
        }
        self.observability.cycle_data_file = "test_cycle_data.log"
        with open(self.observability.cycle_data_file, "w") as f:
            f.write(json.dumps(self.test_cycle_data_running) + "\n")
            f.write(json.dumps(self.test_cycle_data_completed) + "\n")
            f.write(json.dumps(self.test_cycle_data_failed) + "\n")


    def tearDown(self):
        import os
        if os.path.exists(self.observability.cycle_data_file):
            os.remove(self.observability.cycle_data_file)


    def test_read_cycle_data_running(self):
         with open(self.observability.cycle_data_file, "r") as f:
            data = json.loads(f.readline())
            self.assertEqual(data["status"], "running")


    def test_read_cycle_data_completed(self):
        with open(self.observability.cycle_data_file, "r") as f:
            f.readline() # skip running
            data = json.loads(f.readline())
            self.assertEqual(data["status"], "completed")

    def test_cycle_status_endpoint_running(self):
        response = client.get("/cycle/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "running")
        self.assertEqual(data["phase"], "analyzing")

    def test_cycle_status_endpoint_completed(self):
        with open(self.observability.cycle_data_file, "w") as f:
            f.write(json.dumps(self.test_cycle_data_completed) + "\n")
        response = client.get("/cycle/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "completed")

    def test_cycle_status_endpoint_failed(self):
        with open(self.observability.cycle_data_file, "w") as f:
            f.write(json.dumps(self.test_cycle_data_failed) + "\n")
        response = client.get("/cycle/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "failed")

    def test_cycle_history_endpoint(self):
        response = client.get("/cycle/history")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)  # completed and failed cycles
        self.assertEqual(data[0]["status"], "completed")
        self.assertEqual(data[1]["status"], "failed")

    def test_cycle_history_endpoint_limit(self):
         response = client.get("/cycle/history?limit=1")
         self.assertEqual(response.status_code, 200)
         data = response.json()
         self.assertEqual(len(data), 1)
```