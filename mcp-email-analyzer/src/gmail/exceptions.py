# src/gmail/exceptions.py
"""
Custom exceptions for Gmail integration module.
"""
from typing import Optional, Dict, Any


class GmailBaseException(Exception):
    """Base exception for all Gmail-related errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class GmailAuthenticationError(GmailBaseException):
    """Raised when Gmail authentication fails."""
    
    def __init__(self, message: str = "Gmail authentication failed", 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class GmailAuthorizationError(GmailBaseException):
    """Raised when Gmail authorization/permissions are insufficient."""
    
    def __init__(self, message: str = "Insufficient Gmail permissions", 
                 scopes_required: Optional[list] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.scopes_required = scopes_required or []


class GmailRateLimitError(GmailBaseException):
    """Raised when Gmail API rate limits are exceeded."""
    
    def __init__(self, message: str = "Gmail API rate limit exceeded",
                 retry_after: Optional[int] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.retry_after = retry_after


class GmailQuotaExceededError(GmailBaseException):
    """Raised when Gmail API quota is exceeded."""
    
    def __init__(self, message: str = "Gmail API quota exceeded",
                 quota_type: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.quota_type = quota_type


class GmailConnectionError(GmailBaseException):
    """Raised when connection to Gmail API fails."""
    
    def __init__(self, message: str = "Failed to connect to Gmail API",
                 status_code: Optional[int] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.status_code = status_code


class GmailTimeoutError(GmailBaseException):
    """Raised when Gmail API request times out."""
    
    def __init__(self, message: str = "Gmail API request timed out",
                 timeout_duration: Optional[int] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.timeout_duration = timeout_duration


class GmailDataError(GmailBaseException):
    """Raised when Gmail data parsing or validation fails."""
    
    def __init__(self, message: str = "Gmail data processing error",
                 field_name: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.field_name = field_name


class GmailMessageNotFoundError(GmailBaseException):
    """Raised when requested Gmail message is not found."""
    
    def __init__(self, message_id: str,
                 message: str = "Gmail message not found",
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.message_id = message_id


class GmailBatchOperationError(GmailBaseException):
    """Raised when Gmail batch operation fails."""
    
    def __init__(self, message: str = "Gmail batch operation failed",
                 failed_count: int = 0,
                 total_count: int = 0,
                 failed_items: Optional[list] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.failed_count = failed_count
        self.total_count = total_count
        self.failed_items = failed_items or []


class GmailConfigurationError(GmailBaseException):
    """Raised when Gmail configuration is invalid."""
    
    def __init__(self, message: str = "Invalid Gmail configuration",
                 config_field: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.config_field = config_field


class GmailCacheError(GmailBaseException):
    """Raised when Gmail cache operations fail."""
    
    def __init__(self, message: str = "Gmail cache operation failed",
                 cache_key: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.cache_key = cache_key


# Exception mapping for Google API errors
GOOGLE_API_ERROR_MAPPING = {
    400: GmailDataError,
    401: GmailAuthenticationError,
    403: GmailAuthorizationError,
    404: GmailMessageNotFoundError,
    429: GmailRateLimitError,
    500: GmailConnectionError,
    503: GmailConnectionError,
    504: GmailTimeoutError,
}


def map_google_api_error(error_code: int, error_message: str, 
                        details: Optional[Dict[str, Any]] = None) -> GmailBaseException:
    """Map Google API error codes to custom Gmail exceptions."""
    exception_class = GOOGLE_API_ERROR_MAPPING.get(error_code, GmailBaseException)
    return exception_class(error_message, details)