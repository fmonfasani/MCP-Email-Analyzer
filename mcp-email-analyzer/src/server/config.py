"""Configuration management using Pydantic Settings."""

from typing import List, Optional
from pydantic import BaseSettings, Field
from pathlib import Path
from typing import List
from pydantic import BaseSettings, Field

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

"""
Extended configuration for Gmail integration
"""

# src/server/config.py (expandir - agregar a la configuración existente)
"""
Extended configuration for Gmail integration
"""
from typing import List
from pydantic import BaseSettings, Field


class GmailSettings(BaseSettings):
    """Gmail API configuration settings"""
    
    credentials_path: str = Field(
        default="credentials.json",
        description="Path to OAuth2 credentials JSON file"
    )
    
    token_path: str = Field(
        default="token.json", 
        description="Path to store OAuth2 token"
    )
    
    scopes: List[str] = Field(
        default=["https://www.googleapis.com/auth/gmail.modify"],
        description="Gmail API scopes for authentication"
    )
    
    max_results: int = Field(
        default=100,
        ge=1,
        le=500,
        description="Maximum number of emails to fetch per request"
    )
    
    cache_ttl: int = Field(
        default=300,
        ge=0,
        description="Cache TTL in seconds for email data"
    )
    
    batch_size: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Batch size for concurrent email fetching"
    )
    
    retry_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of retry attempts for failed requests"
    )
    
    rate_limit_delay: float = Field(
        default=1.0,
        ge=0.1,
        description="Delay between requests to avoid rate limiting"
    )
    
    enable_compression: bool = Field(
        default=True,
        description="Enable GZIP compression for API requests"
    )
    
    timeout: int = Field(
        default=30,
        ge=5,
        description="Request timeout in seconds"
    )
    
    class Config:
        env_prefix = "GMAIL_"
        case_sensitive = False


# Agregar a la configuración principal del server
class Settings(BaseSettings):
    """Main application settings"""
    
    # ... otras configuraciones existentes ...
    
    # Gmail settings
    gmail: GmailSettings = GmailSettings()
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()