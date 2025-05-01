import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # OpenAI API Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")  # Your OpenAI API key for authentication
    
    # AI Model Parameters
    max_tokens: int = int(os.getenv("MAX_TOKENS", "2000"))  # Maximum length of AI responses
    temperature_founder: float = float(os.getenv("TEMPERATURE_FOUNDER", "0.7"))  # Creativity level for Founder AI (0.0-1.0)
    temperature_developer: float = float(os.getenv("TEMPERATURE_DEVELOPER", "0.2"))  # Precision level for Developer AI (0.0-1.0)
    
    # System Configuration
    environment: str = os.getenv("ENVIRONMENT", "development")  # Current environment (development/production)
    log_level: str = os.getenv("LOG_LEVEL", "INFO")  # Logging verbosity level
    
    class Config:
        env_file = ".env"  # Path to environment variables file

settings = Settings()  # Global settings instance 