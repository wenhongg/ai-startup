"""
Protected file - DO NOT MODIFY
This file contains rate limiting configuration for API calls.
"""

from typing import Dict, Any
import time
from datetime import datetime, timedelta
import logging

class RateLimiter:
    """Rate limiter for API calls."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Gemini API rate limits (free tier)
        self.gemini_limits = {
            "requests_per_minute": 100,  # 15 requests per minute
            "tokens_per_minute": 30000,  # 30k tokens per minute
            "concurrent_requests": 1,    # 1 concurrent request
        }
        
        # GitHub API rate limits
        self.github_limits = {
            "requests_per_hour": 100,     # 10 requests per hour
            "concurrent_requests": 1,    # 1 concurrent request
        }
        
        # Usage tracking
        self.usage: Dict[str, Dict[str, Any]] = {
            "gemini": {
                "requests": [],
                "tokens": 0,
                "last_reset": datetime.now(),
            },
            "github": {
                "requests": [],
                "last_reset": datetime.now(),
            }
        }
    
    def _check_gemini_limits(self) -> bool:
        """Check if Gemini API call is allowed."""
        now = datetime.now()
        
        # Reset counters if needed
        if (now - self.usage["gemini"]["last_reset"]) > timedelta(minutes=1):
            self.usage["gemini"]["requests"] = []
            self.usage["gemini"]["tokens"] = 0
            self.usage["gemini"]["last_reset"] = now
            self.logger.info("Gemini rate limits reset")
        
        # Check request limit
        if len(self.usage["gemini"]["requests"]) >= self.gemini_limits["requests_per_minute"]:
            self.logger.warning(f"Gemini request limit reached: {len(self.usage['gemini']['requests'])}/{self.gemini_limits['requests_per_minute']} requests")
            return False
        
        # Check token limit
        if self.usage["gemini"]["tokens"] >= self.gemini_limits["tokens_per_minute"]:
            self.logger.warning(f"Gemini token limit reached: {self.usage['gemini']['tokens']}/{self.gemini_limits['tokens_per_minute']} tokens")
            return False
        
        return True
    
    def _check_github_limits(self) -> bool:
        """Check if GitHub API call is allowed."""
        now = datetime.now()
        
        # Reset counters if needed
        if (now - self.usage["github"]["last_reset"]) > timedelta(hours=1):
            self.usage["github"]["requests"] = []
            self.usage["github"]["last_reset"] = now
            self.logger.info("GitHub rate limits reset")
        
        # Check request limit
        if len(self.usage["github"]["requests"]) >= self.github_limits["requests_per_hour"]:
            self.logger.warning(f"GitHub request limit reached: {len(self.usage['github']['requests'])}/{self.github_limits['requests_per_hour']} requests")
            return False
        
        return True
    
    def check_limits(self, api: str) -> bool:
        """Check if API call is allowed."""
        if api == "gemini":
            return self._check_gemini_limits()
        elif api == "github":
            return self._check_github_limits()
        return False
    
    def record_request(self, api: str, tokens: int = 0):
        """Record an API request."""
        now = datetime.now()
        
        if api == "gemini":
            self.usage["gemini"]["requests"].append(now)
            self.usage["gemini"]["tokens"] += tokens
            self.logger.info(f"Recorded Gemini request. Total requests: {len(self.usage['gemini']['requests'])}, Total tokens: {self.usage['gemini']['tokens']}")
        elif api == "github":
            self.usage["github"]["requests"].append(now)
            self.logger.info(f"Recorded GitHub request. Total requests: {len(self.usage['github']['requests'])}")
    
    def wait_if_needed(self, api: str):
        """Wait if rate limit would be exceeded."""
        self.logger.info(f"Checking rate limits for {api}...")
        while not self.check_limits(api):
            self.logger.warning(f"Rate limit reached for {api}. Waiting...")
            time.sleep(1)
        self.logger.info(f"Rate limit check passed for {api}")
    
    def cleanup(self):
        """Clean up old request records and reset counters."""
        now = datetime.now()
        
        # Clean up Gemini requests older than 1 minute
        self.usage["gemini"]["requests"] = [
            req for req in self.usage["gemini"]["requests"]
            if (now - req) <= timedelta(minutes=1)
        ]
        
        # Clean up GitHub requests older than 1 hour
        self.usage["github"]["requests"] = [
            req for req in self.usage["github"]["requests"]
            if (now - req) <= timedelta(hours=1)
        ]
        
        self.logger.info("Cleaned up old request records")

# Create a singleton instance
rate_limiter = RateLimiter() 