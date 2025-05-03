"""
Protected file - DO NOT MODIFY
This file contains rate limiting configuration for API calls.
"""

from typing import Dict, Any
import time
from datetime import datetime, timedelta
import asyncio

class RateLimiter:
    """Rate limiter for API calls."""
    
    def __init__(self):
        # Gemini API rate limits (free tier)
        self.gemini_limits = {
            "requests_per_minute": 15,  # 15 requests per minute
            "tokens_per_minute": 30000,  # 30k tokens per minute
            "concurrent_requests": 1,    # 1 concurrent request
        }
        
        # GitHub API rate limits
        self.github_limits = {
            "requests_per_hour": 10,     # 10 requests per hour
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
        
        # Check request limit
        if len(self.usage["gemini"]["requests"]) >= self.gemini_limits["requests_per_minute"]:
            return False
        
        # Check token limit
        if self.usage["gemini"]["tokens"] >= self.gemini_limits["tokens_per_minute"]:
            return False
        
        return True
    
    def _check_github_limits(self) -> bool:
        """Check if GitHub API call is allowed."""
        now = datetime.now()
        
        # Reset counters if needed
        if (now - self.usage["github"]["last_reset"]) > timedelta(hours=1):
            self.usage["github"]["requests"] = []
            self.usage["github"]["last_reset"] = now
        
        # Check request limit
        if len(self.usage["github"]["requests"]) >= self.github_limits["requests_per_hour"]:
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
        elif api == "github":
            self.usage["github"]["requests"].append(now)
    
    async def wait_if_needed(self, api: str):
        """Wait if rate limit would be exceeded."""
        while not self.check_limits(api):
            await asyncio.sleep(1)
    
    def cleanup(self):
        """Clean up old request records and reset counters."""
        now = datetime.now()
        
        # Clean up Gemini records
        if (now - self.usage["gemini"]["last_reset"]) > timedelta(minutes=1):
            self.usage["gemini"]["requests"] = []
            self.usage["gemini"]["tokens"] = 0
            self.usage["gemini"]["last_reset"] = now
        
        # Clean up GitHub records
        if (now - self.usage["github"]["last_reset"]) > timedelta(hours=1):
            self.usage["github"]["requests"] = []
            self.usage["github"]["last_reset"] = now

# Create a singleton instance
rate_limiter = RateLimiter() 