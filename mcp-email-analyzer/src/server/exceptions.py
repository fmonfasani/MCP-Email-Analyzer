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

# src/server/exceptions.py (expandir - agregar excepciones específicas de Gmail)
"""
Custom exceptions for the email analyzer application
"""


class EmailAnalyzerError(Exception):
    """Base exception for email analyzer"""
    pass


class EmailNotFoundError(EmailAnalyzerError):
    """Raised when an email is not found"""
    pass


class EmailServiceError(EmailAnalyzerError):
    """Raised when email service operations fail"""
    pass


class AuthenticationError(EmailAnalyzerError):
    """Raised when authentication fails"""
    pass


class RateLimitError(EmailAnalyzerError):
    """Raised when API rate limits are exceeded"""
    pass


class ConfigurationError(EmailAnalyzerError):
    """Raised when configuration is invalid"""
    pass


class ValidationError(EmailAnalyzerError):
    """Raised when data validation fails"""
    pass


# Gmail-specific exceptions
class GmailAuthError(AuthenticationError):
    """Gmail authentication specific errors"""
    pass


class GmailAPIError(EmailServiceError):
    """Gmail API specific errors"""
    
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class GmailQuotaExceededError(RateLimitError):
    """Gmail API quota exceeded"""
    pass


class GmailPermissionError(EmailServiceError):
    """Gmail permission/scope errors"""
    pass


class AttachmentError(EmailServiceError):
    """Attachment processing errors"""
    pass


class EmailParsingError(EmailServiceError):
    """Email parsing/mapping errors"""
    pass


class CacheError(EmailAnalyzerError):
    """Cache operation errors"""
    pass


class NetworkError(EmailServiceError):
    """Network connectivity errors"""
    pass


class TimeoutError(EmailServiceError):
    """Request timeout errors"""
    pass