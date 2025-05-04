"""
Base class for AI agents in the system.
"""

import google.generativeai as genai
from typing import Optional, Dict, Any
import os
from ..config import settings

class BaseAgent:
    """Base class for all AI agents in the system."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-lite-001"):
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
        
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate a response from the AI model.
        
        Args:
            prompt: The input prompt for the model
            **kwargs: Additional parameters to be included in the prompt
            
        Returns:
            The generated response text
        """
        try:
            # Format the prompt with any additional parameters
            formatted_prompt = prompt
            if kwargs:
                formatted_prompt += "\n\nAdditional context:\n"
                for key, value in kwargs.items():
                    formatted_prompt += f"{key}: {value}\n"
            
            # Add system prompt if available
            if self.system_prompt:
                formatted_prompt = f"{self.system_prompt}\n\n{formatted_prompt}"
            
            # Generate the response
            response = self.model.generate_content(formatted_prompt)
            
            if response and response.text:
                # Split response into lines and remove lines that start with ``` at beginning or end
                lines = response.text.split('\n')
                while lines and lines[0].strip().startswith('```'):
                    lines.pop(0)
                while lines and lines[-1].strip().startswith('```'):
                    lines.pop()
                return '\n'.join(lines)
            else:
                raise Exception("No response generated")
                
        except Exception as e:
            print(f"Error generating response: {e}")
            raise