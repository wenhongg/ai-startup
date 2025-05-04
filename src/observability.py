import logging
import time
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class Observability:
    def __init__(self):
        self.cycle_data: Dict[str, Any] = {
            "stage": "idle",
            "start_time": None,
            "end_time": None,
            "proposal_title": None,
            "proposal_description": None,
            "pr_url": None,
            "errors": [],
        }

    def start_stage(self, stage: str, proposal_title: Optional[str] = None, proposal_description: Optional[str] = None, pr_url: Optional[str] = None):
        if self.cycle_data["stage"] != "idle":
            logger.warning(f"Cycle stage already in progress. Current stage: {self.cycle_data['stage']}. Attempting to start stage: {stage}")
            return

        self.cycle_data["stage"] = stage
        self.cycle_data["start_time"] = time.time()
        self.cycle_data["proposal_title"] = proposal_title
        self.cycle_data["proposal_description"] = proposal_description
        self.cycle_data["pr_url"] = pr_url
        self.cycle_data["errors"] = []
        logger.info(f"Starting stage: {stage}. Proposal: {proposal_title if proposal_title else 'None'}")

    def end_stage(self):
        if self.cycle_data["stage"] == "idle":
            logger.warning("Attempting to end stage when no stage is active.")
            return

        self.cycle_data["end_time"] = time.time()
        stage = self.cycle_data["stage"]
        self.cycle_data["stage"] = "idle"
        logger.info(f"Ending stage: {stage}. Duration: {self._calculate_duration()} seconds")
        self.reset_proposal_info()

    def record_error(self, error_message: str):
        self.cycle_data["errors"].append(error_message)
        logger.error(f"Error during stage {self.cycle_data['stage']}: {error_message}")

    def get_cycle_data(self) -> Dict[str, Any]:
        return self.cycle_data

    def _calculate_duration(self) -> Optional[float]:
        if self.cycle_data["start_time"] is not None and self.cycle_data["end_time"] is not None:
            return self.cycle_data["end_time"] - self.cycle_data["start_time"]
        elif self.cycle_data["start_time"] is not None:
            return time.time() - self.cycle_data["start_time"]
        else:
            return None

    def reset_proposal_info(self):
        self.cycle_data["proposal_title"] = None
        self.cycle_data["proposal_description"] = None
        self.cycle_data["pr_url"] = None