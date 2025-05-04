```python
"""
System orchestrator that coordinates the improvement cycle.
"""

from typing import Dict, Any, List
from .rate_limits import RateLimiter
from .code_manager import CodeManager
from .agents.founder import FounderAI
from .agents.developer import DeveloperAI
from .agents.code_reader import CodeReader
from .config import settings
import time
from flask import Flask, jsonify, abort

class Observability:
    """Handles logging and cycle report generation."""
    def __init__(self):
        self.logs = {}  # cycle_id: list of log messages
        self.summaries = {} # cycle_id: cycle summary data

    def log_message(self, cycle_id: str, message: str):
        """Logs a message for a specific cycle."""
        if cycle_id not in self.logs:
            self.logs[cycle_id] = []
        self.logs[cycle_id].append(message)

    def set_cycle_summary(self, cycle_id: str, summary_data: Dict[str, Any]):
        """Sets summary data for a specific cycle."""
        self.summaries[cycle_id] = summary_data

    def get_cycle_report(self, cycle_id: str) -> Dict[str, Any]:
        """Retrieves the cycle report, including logs and summary."""
        if cycle_id not in self.logs or cycle_id not in self.summaries:
            return None

        report = {
            "logs": self.logs[cycle_id],
            "summary": self.summaries[cycle_id]
        }
        return report


class SystemOrchestrator:
    """Coordinates the improvement cycle between AI agents."""
    
    def __init__(self):
        """Initialize the orchestrator with all necessary components."""
        self.rate_limiter = RateLimiter()
        self.code_manager = CodeManager()
        self.code_reader = CodeReader()
        self.founder = FounderAI(self.code_reader)
        self.developer = DeveloperAI(self.code_reader)
        self.observability = Observability()
        self.app = Flask(__name__)
        self.setup_routes()
        
    def setup_routes(self):
        @self.app.route('/cycles/<cycle_id>', methods=['GET'])
        def get_cycle_report(cycle_id):
            report = self.observability.get_cycle_report(cycle_id)
            if report is None:
                abort(404)
            return jsonify(report)

    def run_improvement_cycle(self):
        """Run a complete improvement cycle."""
        cycle_id = str(int(time.time()))  # Use timestamp as cycle ID
        self.observability.log_message(cycle_id, "Running improvement cycle...")
        try:
            # Summarize the repository first
            self.observability.log_message(cycle_id, "Summarizing repository...")
            self.code_reader.summarize_repository()
            
            self.observability.log_message(cycle_id, "Generating proposal...")
            # Get product summaries and generate proposal
            product_summaries = self.code_reader.get_code_summaries()
            proposal = self.founder.generate_proposal(product_summaries)
            
            self.observability.log_message(cycle_id, "Implementing changes...")
            # Developer reviews and implements
            changes, title, description = self.developer.implement_changes(proposal)
            
            # Add the proposal to the changes
            proposal_file = f"proposals/{cycle_id}_proposal.md"
            changes[proposal_file] = f"""# Improvement Proposal

## Title: {title}

## Description:
{description}

## Files to Change:
{chr(10).join(f'- {file}' for file in changes.keys())}

## Original Proposal from Founder:
{proposal}
"""
            
            self.observability.log_message(cycle_id, f"Changes: {changes}")
            self.observability.log_message(cycle_id, f"Title: {title}")
            self.observability.log_message(cycle_id, f"Description: {description}")

            self.observability.log_message(cycle_id, "Creating pull request...")
            # Create pull request with changes
            pr_url = self.code_manager.create_pull_request(changes, title, description)
            self.observability.log_message(cycle_id, f"Created pull request: {pr_url}")
            
            # Set cycle summary data
            summary_data = {
                "title": title,
                "description": description,
                "pull_request_url": pr_url,
                "files_changed": list(changes.keys()),
            }
            self.observability.set_cycle_summary(cycle_id, summary_data)
            
            # Reset caches at the end of the cycle
            self.observability.log_message(cycle_id, "Resetting caches...")
            self.code_reader.reset()
            self.founder.reset()
            
        except Exception as e:
            self.observability.log_message(cycle_id, f"Error in improvement cycle: {e}")
            raise
        
    def start_api(self, host='0.0.0.0', port=5000, debug=False):
        self.app.run(host=host, port=port, debug=debug)
```