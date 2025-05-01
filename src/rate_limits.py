"""
Rate limiting configuration for API calls.
This file is protected and should not be modified by the AI agents.
"""

from typing import Dict, Any
import time
from datetime import datetime, timedelta
import asyncio

class RateLimiter:
    def __init__(self):
        # OpenAI API rate limits - set for very low cost tier
        # Assuming GPT-4-turbo at $0.01/1K tokens
        # Target: ~$10/month = ~1M tokens/month = ~33K tokens/day
        self.openai_limits = {
            "requests_per_minute": 1,      # 1 request per minute (sequential processing)
            "tokens_per_minute": 2000,     # 2K tokens per minute
            "concurrent_requests": 1,       # Only 1 concurrent request
            "daily_token_limit": 33000,    # 33K tokens per day
            "monthly_token_limit": 1000000  # 1M tokens per month
        }
        
        # GitHub API rate limits - very conservative since we only make a few requests per day
        self.github_limits = {
            "requests_per_hour": 10,       # 10 requests per hour is more than enough
            "concurrent_requests": 1        # Only 1 concurrent request
        }
        
        # Tracking variables
        self.openai_requests: Dict[str, Any] = {
            "last_reset": datetime.now(),
            "request_count": 0,
            "token_count": 0,
            "concurrent_count": 0,
            "daily_tokens": 0,
            "monthly_tokens": 0,
            "last_daily_reset": datetime.now(),
            "last_monthly_reset": datetime.now()
        }
        
        self.github_requests: Dict[str, Any] = {
            "last_reset": datetime.now(),
            "request_count": 0,
            "concurrent_count": 0
        }
    
    async def check_openai_limit(self, estimated_tokens: int = 0) -> bool:
        """
        Check if OpenAI API call is allowed based on rate limits.
        Returns True if the call is allowed, False if it should be delayed.
        """
        now = datetime.now()
        
        # Reset counters if a minute has passed
        if now - self.openai_requests["last_reset"] > timedelta(minutes=1):
            self.openai_requests["last_reset"] = now
            self.openai_requests["request_count"] = 0
            self.openai_requests["token_count"] = 0
        
        # Reset daily token count if a day has passed
        if now - self.openai_requests["last_daily_reset"] > timedelta(days=1):
            self.openai_requests["last_daily_reset"] = now
            self.openai_requests["daily_tokens"] = 0
        
        # Reset monthly token count if a month has passed
        if now - self.openai_requests["last_monthly_reset"] > timedelta(days=30):
            self.openai_requests["last_monthly_reset"] = now
            self.openai_requests["monthly_tokens"] = 0
        
        # Check if we've hit any limits
        if (self.openai_requests["request_count"] >= self.openai_limits["requests_per_minute"] or
            self.openai_requests["token_count"] + estimated_tokens > self.openai_limits["tokens_per_minute"] or
            self.openai_requests["concurrent_count"] >= self.openai_limits["concurrent_requests"] or
            self.openai_requests["daily_tokens"] + estimated_tokens > self.openai_limits["daily_token_limit"] or
            self.openai_requests["monthly_tokens"] + estimated_tokens > self.openai_limits["monthly_token_limit"]):
            return False
        
        return True
    
    async def check_github_limit(self) -> bool:
        """
        Check if GitHub API call is allowed based on rate limits.
        Returns True if the call is allowed, False if it should be delayed.
        """
        now = datetime.now()
        
        # Reset counters if an hour has passed
        if now - self.github_requests["last_reset"] > timedelta(hours=1):
            self.github_requests["last_reset"] = now
            self.github_requests["request_count"] = 0
        
        # Check if we've hit any limits
        if (self.github_requests["request_count"] >= self.github_limits["requests_per_hour"] or
            self.github_requests["concurrent_count"] >= self.github_limits["concurrent_requests"]):
            return False
        
        return True
    
    def record_openai_request(self, tokens_used: int):
        """Record an OpenAI API request"""
        self.openai_requests["request_count"] += 1
        self.openai_requests["token_count"] += tokens_used
        self.openai_requests["daily_tokens"] += tokens_used
        self.openai_requests["monthly_tokens"] += tokens_used
        self.openai_requests["concurrent_count"] += 1
    
    def record_openai_completion(self):
        """Record completion of an OpenAI API request"""
        self.openai_requests["concurrent_count"] -= 1
    
    def record_github_request(self):
        """Record a GitHub API request"""
        self.github_requests["request_count"] += 1
        self.github_requests["concurrent_count"] += 1
    
    def record_github_completion(self):
        """Record completion of a GitHub API request"""
        self.github_requests["concurrent_count"] -= 1
    
    async def wait_for_openai(self, estimated_tokens: int = 0):
        """Wait until OpenAI API call is allowed"""
        while not await self.check_openai_limit(estimated_tokens):
            # If we've hit daily or monthly limits, wait longer
            if (self.openai_requests["daily_tokens"] + estimated_tokens > self.openai_limits["daily_token_limit"] or
                self.openai_requests["monthly_tokens"] + estimated_tokens > self.openai_limits["monthly_token_limit"]):
                await asyncio.sleep(60)  # Wait a minute before checking again
            else:
                await asyncio.sleep(1)  # Wait 1 second before checking again
    
    async def wait_for_github(self):
        """Wait until GitHub API call is allowed"""
        while not await self.check_github_limit():
            await asyncio.sleep(1)  # Wait 1 second before checking again 