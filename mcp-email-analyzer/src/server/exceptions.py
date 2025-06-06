"""Custom exceptions for MCP Email Analyzer."""

from typing import Optional, Dict, Any


class MCPEmailAnalyzerError(Exception):
    """Base exception for MCP Email Analyzer."""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class GmailAPIError(MCPEmailAnalyzerError):
    """Gmail API related errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="GMAIL_API_ERROR", 
            details=details
        )


class EmailNotFoundError(MCPEmailAnalyzerError):
    """Email not found error."""
    
    def __init__(self, email_id: str):
        super().__init__(
            message=f"Email with ID '{email_id}' not found",
            error_code="EMAIL_NOT_FOUND",
            details={"email_id": email_id}
        )


class AuthenticationError(MCPEmailAnalyzerError):
    """Authentication related errors."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR"
        )


class AnalysisError(MCPEmailAnalyzerError):
    """Email analysis related errors."""
    
    def __init__(self, message: str, email_id: Optional[str] = None):
        details = {"email_id": email_id} if email_id else {}
        super().__init__(
            message=message,
            error_code="ANALYSIS_ERROR",
            details=details
        )


class ConfigurationError(MCPEmailAnalyzerError):
    """Configuration related errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {"config_key": config_key} if config_key else {}
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=details
        )


class RateLimitError(MCPEmailAnalyzerError):
    """Rate limit exceeded error."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            details=details
        )