"""Configuration management using Pydantic Settings."""

from typing import List, Optional
from pydantic import BaseSettings, Field
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Gmail API Configuration
    gmail_credentials_path: str = Field(
        default="credentials.json",
        description="Path to Gmail API credentials file"
    )
    gmail_token_path: str = Field(
        default="token.json", 
        description="Path to Gmail API token file"
    )
    gmail_scopes: List[str] = Field(
        default=[
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.modify"
        ],
        description="Gmail API scopes"
    )
    
    # MCP Server Configuration
    mcp_server_host: str = Field(
        default="localhost",
        description="MCP server host"
    )
    mcp_server_port: int = Field(
        default=8080,
        description="MCP server port"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    log_format: str = Field(
        default="json",
        description="Logging format"
    )
    
    # Analysis Configuration
    default_email_limit: int = Field(
        default=50,
        description="Default limit for email queries"
    )
    analysis_confidence_threshold: float = Field(
        default=0.7,
        description="Minimum confidence threshold for analysis results"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()