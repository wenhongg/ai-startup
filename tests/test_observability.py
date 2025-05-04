```python
import unittest
import json
import os
import shutil
from unittest.mock import patch
from observability import Observability

class TestObservability(unittest.TestCase):

    def setUp(self):
        self.test_dir = "test_logs"
        self.observability = Observability(log_dir=self.test_dir)
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def create_cycle_log(self, filename, cycle_data):
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, "w") as f:
            json.dump(cycle_data, f)

    def test_read_cycle_data_success(self):
        cycle_data = {
            "cycle_id": "cycle-123",
            "start_time": "2024-01-01T00:00:00Z",
            "end_time": "2024-01-01T01:00:00Z",
            "status": "completed",
            "summary": "Implemented feature X",
            "phase_data": {
                "analyzing": {"start": "...", "end": "...", "details": "..."}
            }
        }
        self.create_cycle_log("cycle-123.json", cycle_data)
        data = self.observability.read_cycle_data("cycle-123.json")
        self.assertEqual(data, cycle_data)

    def test_read_cycle_data_file_not_found(self):
        data = self.observability.read_cycle_data("nonexistent.json")
        self.assertIsNone(data)

    def test_read_cycle_data_invalid_json(self):
        filepath = os.path.join(self.test_dir, "invalid.json")
        with open(filepath, "w") as f:
            f.write("This is not JSON")
        data = self.observability.read_cycle_data("invalid.json")
        self.assertIsNone(data)

    def test_get_latest_cycle_status_no_logs(self):
        status = self.observability.get_latest_cycle_status()
        self.assertEqual(status, {"status": "idle"})

    def test_get_latest_cycle_status_running(self):
        cycle_data = {
            "cycle_id": "cycle-456",
            "start_time": "2024-01-02T10:00:00Z",
            "status": "running",
            "phase": "analyzing",
            "phase_data": {"analyzing": {"start": "...", "details": "..."}}
        }
        self.create_cycle_log("cycle-456.json", cycle_data)
        status = self.observability.get_latest_cycle_status()
        self.assertEqual(status["status"], "running")
        self.assertEqual(status["phase"], "analyzing")
        self.assertEqual(status["cycle_id"], "cycle-456")

    def test_get_latest_cycle_status_completed(self):
        cycle_data = {
            "cycle_id": "cycle-789",
            "start_time": "2024-01-03T08:00:00Z",
            "end_time": "2024-01-03T09:00:00Z",
            "status": "completed",
            "summary": "Implemented feature Y",
            "phase_data": {
                "analyzing": {"start": "...", "end": "...", "details": "..."}
            }
        }
        self.create_cycle_log("cycle-789.json", cycle_data)
        status = self.observability.get_latest_cycle_status()
        self.assertEqual(status["status"], "completed")
        self.assertEqual(status["cycle_id"], "cycle-789")

    def test_get_latest_cycle_status_failed(self):
         cycle_data = {
            "cycle_id": "cycle-101",
            "start_time": "2024-01-04T12:00:00Z",
            "end_time": "2024-01-04T13:00:00Z",
            "status": "failed",
            "failure_reason": "Error during implementation",
            "phase_data": {
                "analyzing": {"start": "...", "end": "...", "details": "..."}
            }
        }
         self.create_cycle_log("cycle-101.json", cycle_data)
         status = self.observability.get_latest_cycle_status()
         self.assertEqual(status["status"], "failed")
         self.assertEqual(status["cycle_id"], "cycle-101")
         self.assertEqual(status["failure_reason"], "Error during implementation")

    def test_get_cycle_history_empty(self):
        history = self.observability.get_cycle_history(limit=5)
        self.assertEqual(history, [])

    def test_get_cycle_history_success(self):
        cycle_data_1 = {
            "cycle_id": "cycle-201",
            "start_time": "2024-01-05T10:00:00Z",
            "end_time": "2024-01-05T11:00:00Z",
            "status": "completed",
            "summary": "Implemented feature Z",
        }
        cycle_data_2 = {
            "cycle_id": "cycle-202",
            "start_time": "2024-01-06T12:00:00Z",
            "end_time": "2024-01-06T13:00:00Z",
            "status": "failed",
            "failure_reason": "Failed to parse data",
        }
        self.create_cycle_log("cycle-201.json", cycle_data_1)
        self.create_cycle_log("cycle-202.json", cycle_data_2)

        history = self.observability.get_cycle_history(limit=2)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["cycle_id"], "cycle-202")
        self.assertEqual(history[1]["cycle_id"], "cycle-201")

    def test_get_cycle_history_limit(self):
        for i in range(5):
            cycle_data = {
                "cycle_id": f"cycle-{300+i}",
                "start_time": f"2024-01-0{i+7}T10:00:00Z",
                "end_time": f"2024-01-0{i+7}T11:00:00Z",
                "status": "completed",
                "summary": f"Implemented feature {i}",
            }
            self.create_cycle_log(f"cycle-{300+i}.json", cycle_data)

        history = self.observability.get_cycle_history(limit=3)
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]["cycle_id"], "cycle-304")
        self.assertEqual(history[2]["cycle_id"], "cycle-302")

    def test_get_cycle_history_invalid_logs(self):
        self.create_cycle_log("invalid.json", "not json")
        history = self.observability.get_cycle_history(limit=5)
        self.assertEqual(history, [])
```