from typing import Dict, Any, Optional
import logging
import asyncio
from .agents import FounderAI, DeveloperAI
from .code_manager import CodeManager
from .safety_checker import SafetyChecker
from src.rate_limits import RateLimiter

class SystemOrchestrator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rate_limiter = RateLimiter()
        self.founder_ai = FounderAI()
        self.developer_ai = DeveloperAI()
        self.safety_checker = SafetyChecker()
        self.code_manager = CodeManager()
        
        # Share rate limiter instance
        self.founder_ai.rate_limiter = self.rate_limiter
        self.developer_ai.rate_limiter = self.rate_limiter
        self.code_manager.rate_limiter = self.rate_limiter
        
    async def run_improvement_cycle(self) -> Dict[str, Any]:
        """Run a complete improvement cycle with rate limiting"""
        try:
            # Step 1: Analysis by Founder AI
            self.logger.info("Starting improvement cycle - Founder AI analysis")
            analysis = await self.founder_ai.analyze_system()
            
            # Step 2: Proposal generation
            self.logger.info("Generating improvement proposal")
            proposal = await self.founder_ai.generate_proposal(analysis)
            
            # Step 3: Review and planning by Developer AI
            self.logger.info("Developer AI reviewing proposal")
            plan = await self.developer_ai.review_proposal(proposal)
            
            # Step 4: Safety check
            self.logger.info("Running safety checks")
            is_valid, issues = await self.safety_checker.validate_plan(plan)
            if not is_valid:
                self.logger.warning(f"Safety check failed: {issues}")
                return {"status": "failed", "reason": "safety_check_failed", "issues": issues}
            
            # Step 5: Implementation
            self.logger.info("Implementing changes")
            changes, title, description = await self.developer_ai.implement_changes(plan)
            
            # Step 6: Testing with fixing loop
            max_attempts = 3
            attempt = 0
            while attempt < max_attempts:
                attempt += 1
                self.logger.info(f"Testing changes (attempt {attempt}/{max_attempts})")
                
                is_valid, issues = await self.safety_checker.test_changes(changes)
                if is_valid:
                    break
                    
                self.logger.warning(f"Test failed: {issues}")
                changes, title, description = await self.developer_ai.fix_issues(changes, issues)
            
            if not is_valid:
                return {"status": "failed", "reason": "test_failed", "issues": issues}
            
            # Step 7: Create pull request
            self.logger.info("Creating pull request")
            branch_name = await self.code_manager.create_pull_request(changes, title, description)
            
            return {
                "status": "success",
                "branch": branch_name,
                "title": title,
                "description": description,
                "attempts": attempt
            }
            
        except Exception as e:
            self.logger.error(f"Improvement cycle failed: {str(e)}")
            return {"status": "failed", "reason": "error", "error": str(e)} 