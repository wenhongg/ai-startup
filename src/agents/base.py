from openai import AsyncOpenAI
from typing import Dict, Any, Optional
import os
from ..config import settings
import logging
from src.rate_limits import RateLimiter

class BaseAgent:
    def __init__(self, model: str = "gpt-4-turbo-preview"):
        self.logger = logging.getLogger(__name__)
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.rate_limiter = RateLimiter()
        self.system_prompt = ""
        self.settings = settings
    
    def _load_prompt(self, prompt_file: str) -> str:
        """Load a prompt from a text file"""
        prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", prompt_file)
        try:
            with open(prompt_path, 'r') as f:
                return f.read().strip()
        except Exception as e:
            raise Exception(f"Failed to load prompt from {prompt_file}: {str(e)}")
    
    async def _generate_response(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate a response using the OpenAI API with rate limiting"""
        try:
            # Wait for rate limit before making the API call
            await self.rate_limiter.wait_for_openai(estimated_tokens=max_tokens)
            
            # Record the request
            self.rate_limiter.record_openai_request(max_tokens)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            # Record completion
            self.rate_limiter.record_openai_completion()
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            raise
    
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self._format_prompt(prompt, context)}
        ]
        
        response = await self._generate_response(self._format_prompt(prompt, context))
        return response
    
    def _format_prompt(self, prompt: str, context: Dict[str, Any] = None) -> str:
        if not context:
            return prompt
        return f"{prompt}\n\nContext:\n{context}" 