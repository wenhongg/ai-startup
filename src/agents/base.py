"""
Base class for AI agents in the system.
"""

import google.generativeai as genai
from typing import Optional, Dict, Any
import os
from ..config import settings

class BaseAgent:
    """Base class for all AI agents in the system."""
    
    def __init__(self, model_name: str = "gemini-1.5-pro-002"):
        """Initialize the base agent with a specific model."""
        # Configure the Gemini API
        genai.configure(api_key=settings.gemini_api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel(model_name)
        self.system_prompt = None
        
    def _load_prompt(self, filename: str) -> str:
        """
        Load a prompt from a file in the prompts directory.
        
        Args:
            filename: Name of the prompt file
            
        Returns:
            The prompt text
        """
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", filename)
        try:
            with open(prompt_path, "r") as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error loading prompt {filename}: {e}")
            return ""
        
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate a response from the AI model.
        
        Args:
            prompt: The input prompt for the model
            **kwargs: Additional parameters for the model
            
        Returns:
            The generated response text
        """
        try:
            # Combine system prompt with the input prompt if system prompt exists
            full_prompt = f"{self.system_prompt}\n\n{prompt}" if self.system_prompt else prompt
            response = await self.model.generate_content_async(full_prompt, **kwargs)
            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return ""
    
    async def analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze code and return insights."""
        prompt = f"""
        Analyze the following code and provide insights:
        {code}
        
        Please provide:
        1. Code quality assessment
        2. Potential improvements
        3. Security considerations
        4. Performance implications
        """
        
        response = await self.generate_response(prompt)
        return {
            "analysis": response,
            "code": code
        }
    
    async def suggest_improvements(self, code: str) -> Dict[str, Any]:
        """Suggest improvements for the given code."""
        prompt = f"""
        Suggest improvements for the following code:
        {code}
        
        Please provide:
        1. Specific improvements with explanations
        2. Code examples for each improvement
        3. Potential impact of changes
        """
        
        response = await self.generate_response(prompt)
        return {
            "suggestions": response,
            "code": code
        }
    
    async def review_changes(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        """Review proposed changes."""
        prompt = f"""
        Review the following changes:
        {changes}
        
        Please provide:
        1. Code review comments
        2. Potential issues
        3. Suggestions for improvement
        4. Overall assessment
        """
        
        response = await self.generate_response(prompt)
        return {
            "review": response,
            "changes": changes
        } 