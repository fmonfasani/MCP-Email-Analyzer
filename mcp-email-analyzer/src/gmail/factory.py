# src/gmail/factory.py
"""
Factory for creating Gmail repository instances
"""
import structlog
from typing import Optional

from ..core.interfaces import EmailRepository
from ..server.config import GmailSettings
from ..server.exceptions import ConfigurationError
from .client import GmailRepository

logger = structlog.get_logger(__name__)


class GmailRepositoryFactory:
    """Factory for creating Gmail repository instances"""
    
    _instance: Optional[GmailRepository] = None
    _settings: Optional[GmailSettings] = None
    
    @classmethod
    def create(cls, settings: GmailSettings) -> EmailRepository:
        """
        Create a Gmail repository instance
        
        Args:
            settings: Gmail configuration settings
            
        Returns:
            GmailRepository instance
            
        Raises:
            ConfigurationError: If settings are invalid
        """
        try:
            cls._validate_settings(settings)
            
            # Create new instance if settings changed or no instance exists
            if cls._instance is None or cls._settings != settings:
                logger.info("Creating new Gmail repository instance")
                cls._instance = GmailRepository(settings)
                cls._settings = settings
            
            return cls._instance
            
        except Exception as e:
            logger.error("Failed to create Gmail repository", error=str(e))
            raise ConfigurationError(f"Failed to create Gmail repository: {str(e)}")
    
    @classmethod
    def _validate_settings(cls, settings: GmailSettings) -> None:
        """
        Validate Gmail settings
        
        Args:
            settings: Settings to validate
            
        Raises:
            ConfigurationError: If settings are invalid
        """
        if not settings.credentials_path:
            raise ConfigurationError("Gmail credentials path is required")
        
        if not settings.token_path:
            raise ConfigurationError("Gmail token path is required")
        
        if not settings.scopes:
            raise ConfigurationError("Gmail scopes are required")
        
        if settings.max_results <= 0:
            raise ConfigurationError("Max results must be positive")
        
        if settings.cache_ttl < 0:
            raise ConfigurationError("Cache TTL cannot be negative")
        
        # Validate scopes
        valid_scopes = [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.modify",
            "https://www.googleapis.com/auth/gmail.compose",
            "https://www.googleapis.com/auth/gmail.send"
        ]
        
        for scope in settings.scopes:
            if scope not in valid_scopes:
                logger.warning("Unknown Gmail scope", scope=scope)
    
    @classmethod
    def get_instance(cls) -> Optional[GmailRepository]:
        """
        Get current Gmail repository instance
        
        Returns:
            Current instance or None
        """
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """Reset factory state"""
        cls._instance = None
        cls._settings = None
        logger.info("Gmail repository factory reset")


# Convenience function
def create_gmail_repository(settings: GmailSettings) -> EmailRepository:
    """
    Convenience function to create Gmail repository
    
    Args:
        settings: Gmail settings
        
    Returns:
        EmailRepository instance
    """
    return GmailRepositoryFactory.create(settings)