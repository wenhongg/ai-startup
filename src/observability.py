from typing import Dict, Any, List
import logging
from datetime import datetime
import os

# TODO: Not in use

class Observability:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cycle_data = {
            "start_time": None,
            "analysis": None,
            "proposal": None,
            "implementation_plan": None,
            "changes": None,
            "fix_attempts": [],
            "end_time": None,
            "status": None
        }
        # Ensure logs directory exists
        self.logs_dir = "logs"
        os.makedirs(self.logs_dir, exist_ok=True)
    
    def _get_log_filename(self, prefix: str) -> str:
        """Generate a log filename with the current date"""
        date_str = datetime.now().strftime("%Y%m%d")
        return os.path.join(self.logs_dir, f"{prefix}_{date_str}.txt")
    
    def start_cycle(self):
        """Start tracking a new improvement cycle"""
        self.cycle_data = {
            "start_time": datetime.now(),
            "analysis": None,
            "proposal": None,
            "implementation_plan": None,
            "changes": None,
            "fix_attempts": [],
            "end_time": None,
            "status": None
        }
        self.logger.info("Started new improvement cycle")
    
    def record_analysis(self, analysis: str):
        """Record the system analysis"""
        self.cycle_data["analysis"] = analysis
        self.logger.info("Recorded system analysis")
    
    def record_proposal(self, proposal: str):
        """Record the improvement proposal and save to file"""
        self.cycle_data["proposal"] = proposal
        self.logger.info("Recorded improvement proposal")
        
        # Save proposal to file
        filename = self._get_log_filename("proposal")
        with open(filename, "w") as f:
            f.write(f"Proposal generated at: {datetime.now()}\n\n")
            f.write(proposal)
        self.logger.info(f"Saved proposal to {filename}")
    
    def record_implementation_plan(self, plan: str):
        """Record the implementation plan and save to file"""
        self.cycle_data["implementation_plan"] = plan
        self.logger.info("Recorded implementation plan")
        
        # Save implementation plan to file
        filename = self._get_log_filename("implementation_plan")
        with open(filename, "w") as f:
            f.write(f"Implementation plan generated at: {datetime.now()}\n\n")
            f.write(plan)
        self.logger.info(f"Saved implementation plan to {filename}")
    
    def record_changes(self, changes: Dict[str, Any]):
        """Record the implemented changes"""
        self.cycle_data["changes"] = changes
        self.logger.info("Recorded implemented changes")
    
    def record_fix_attempt(self, issues: List[str], fixed_changes: Dict[str, Any]):
        """Record a fix attempt with the issues and fixed changes"""
        self.cycle_data["fix_attempts"].append({
            "timestamp": datetime.now(),
            "issues": issues,
            "changes": fixed_changes
        })
        self.logger.info(f"Recorded fix attempt {len(self.cycle_data['fix_attempts'])}")
    
    def end_cycle(self, status: str):
        """End the current improvement cycle"""
        self.cycle_data["end_time"] = datetime.now()
        self.cycle_data["status"] = status
        self.logger.info(f"Ended improvement cycle with status: {status}")
    
    def get_cycle_summary(self) -> str:
        """Generate a detailed summary of the improvement cycle"""
        if not self.cycle_data["start_time"]:
            return "No improvement cycle in progress"
        
        summary = []
        summary.append("# Improvement Cycle Summary")
        summary.append(f"\n## Cycle Information")
        summary.append(f"- Start Time: {self.cycle_data['start_time']}")
        summary.append(f"- End Time: {self.cycle_data['end_time']}")
        summary.append(f"- Status: {self.cycle_data['status']}")
        
        if self.cycle_data["analysis"]:
            summary.append("\n## System Analysis")
            summary.append(self.cycle_data["analysis"])
        
        if self.cycle_data["proposal"]:
            summary.append("\n## Improvement Proposal")
            summary.append(self.cycle_data["proposal"])
        
        if self.cycle_data["implementation_plan"]:
            summary.append("\n## Implementation Plan")
            summary.append(self.cycle_data["implementation_plan"])
        
        if self.cycle_data["changes"]:
            summary.append("\n## Implemented Changes")
            summary.append("The following files were modified:")
            for file_path in self.cycle_data["changes"].keys():
                summary.append(f"- {file_path}")
        
        if self.cycle_data["fix_attempts"]:
            summary.append("\n## Fix Attempts")
            for i, attempt in enumerate(self.cycle_data["fix_attempts"], 1):
                summary.append(f"\n### Attempt {i}")
                summary.append(f"- Time: {attempt['timestamp']}")
                summary.append("- Issues Found:")
                for issue in attempt["issues"]:
                    summary.append(f"  - {issue}")
                summary.append("- Changes Made:")
                for file_path in attempt["changes"].keys():
                    summary.append(f"  - {file_path}")
        
        return "\n".join(summary) 