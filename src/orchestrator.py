"""
System orchestrator that coordinates the improvement cycle.
"""

import asyncio
from typing import Dict, Any, List
from .rate_limits import RateLimiter
from .code_manager import CodeManager
from .agents.founder import FounderAI
from .agents.developer import DeveloperAI
from .observability import Observability
from .config import settings

class SystemOrchestrator:
    """Coordinates the improvement cycle between AI agents."""
    
    def __init__(self):
        """Initialize the orchestrator with all necessary components."""
        self.rate_limiter = RateLimiter()
        self.code_manager = CodeManager()
        self.founder = FounderAI()
        self.developer = DeveloperAI(settings.repo_url)
        self.observability = Observability()
        
    async def run_improvement_cycle(self):
        """Run a complete improvement cycle."""
        print("Running improvement cycle...")
        try:
            # Get current code state
            current_code = await self.code_manager.get_current_state()
            
            # Founder proposes improvements
            proposal = await self.founder.generate_proposal()
            
            print(f"Proposal: {proposal}")
            # Below stages in progress.
            # Developer reviews and implements
            # changes, title, description = await self.developer.implement_changes(proposal)
            
            # Apply changes
            # await self.code_manager.apply_changes(changes, title, description)
            
            # Log the cycle
            # self.observability.log_cycle(proposal, changes)
            
        except Exception as e:
            print(f"Error: {e}")
            raise 