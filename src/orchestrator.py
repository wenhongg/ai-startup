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

class SystemOrchestrator:
    """Coordinates the improvement cycle between AI agents."""
    
    def __init__(self):
        """Initialize the orchestrator with all necessary components."""
        self.rate_limiter = RateLimiter()
        self.code_manager = CodeManager()
        self.code_reader = CodeReader()
        self.founder = FounderAI(self.code_reader)
        self.developer = DeveloperAI(self.code_reader)
        
    def run_improvement_cycle(self):
        """Run a complete improvement cycle."""
        print("Running improvement cycle...")
        try:
            # Summarize the repository first
            print("Summarizing repository...")
            self.code_reader.summarize_repository()
            
            print("Generating proposal...")
            # Get product summaries and generate proposal
            product_summaries = self.code_reader.get_code_summaries()
            proposal = self.founder.generate_proposal(product_summaries)
            
            print("Implementing changes...")
            # Developer reviews and implements
            changes, title, description = self.developer.implement_changes(proposal)
            
            # Add the proposal to the changes
            proposal_file = f"proposals/{int(time.time())}_proposal.md"
            changes[proposal_file] = f"""# Improvement Proposal

## Title: {title}

## Description:
{description}

## Files to Change:
{chr(10).join(f'- {file}' for file in changes.keys())}

## Original Proposal from Founder:
{proposal}
"""
            
            print(f"Changes: {changes}")
            print(f"Title: {title}")
            print(f"Description: {description}")

            print("Creating pull request...")
            # Create pull request with changes
            pr_url = self.code_manager.create_pull_request(changes, title, description)
            print(f"Created pull request: {pr_url}")
            
            # Reset caches at the end of the cycle
            print("Resetting caches...")
            self.code_reader.reset()
            self.founder.reset()
            
        except Exception as e:
            print(f"Error in improvement cycle: {e}")
            raise 