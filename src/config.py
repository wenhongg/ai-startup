"""
Configuration settings for the application.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """Application settings."""
    
    # API Keys
    gemini_api_key: str = Field(..., validation_alias="GEMINI_API_KEY")
    github_token: str = Field(..., validation_alias="GITHUB_TOKEN")
    
    # Rate Limits
    gemini_rate_limit: int = Field(default=60, validation_alias="GEMINI_RATE_LIMIT")
    github_rate_limit: int = Field(default=5000, validation_alias="GITHUB_RATE_LIMIT")
    
    # Repository Settings
    repo_url: str = Field(default="https://github.com/wenhongg/ai-startup", validation_alias="REPO_URL")
    branch: str = Field(default="main", validation_alias="BRANCH")
    
    # Logging
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", validation_alias="LOG_FILE")
    
    # Database
    database_url: str = Field(default="sqlite:///ai_startup.db", validation_alias="DATABASE_URL")
    
    # AI Model Parameters
    max_tokens: int = Field(default=2000, validation_alias="MAX_TOKENS")
    temperature_founder: float = Field(default=0.7, validation_alias="TEMPERATURE_FOUNDER")
    temperature_developer: float = Field(default=0.2, validation_alias="TEMPERATURE_DEVELOPER")
    
    # System Configuration
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

# Global settings instance
settings = Settings()

# Example usage:
# If you have an extra field in your .env file like:
# CUSTOM_FIELD=some_value
# You can access it with:
# custom_value = settings.get_extra_field("CUSTOM_FIELD", "default_value") 