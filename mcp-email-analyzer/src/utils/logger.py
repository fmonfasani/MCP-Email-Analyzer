"""Logging configuration for MCP Email Analyzer."""

import sys
import logging
from typing import Any, Dict, Optional

import structlog
from structlog import types


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def add_app_context(logger: types.WrappedLogger, method_name: str, event_dict: types.EventDict) -> types.EventDict:
    """Add application context to log events."""
    event_dict["app"] = "mcp-email-analyzer"
    event_dict["version"] = "0.1.0"
    return event_dict


def add_correlation_id(logger: types.WrappedLogger, method_name: str, event_dict: types.EventDict) -> types.EventDict:
    """Add correlation ID to log events for request tracing."""
    # TODO: Implement correlation ID extraction from context
    # This would typically come from request headers or asyncio context
    return event_dict


def setup_logger(
    level: str = "INFO",
    format_type: str = "json",
    enable_colors: bool = True,
    logger_name: Optional[str] = None
) -> None:
    """Setup structured logging with configurable format."""
    
    # Configure structlog
    processors = [
        add_app_context,
        add_correlation_id,
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.add_logger_name,
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    if format_type.lower() == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.extend([
            structlog.processors.ExceptionPrettyPrinter(),
            structlog.dev.ConsoleRenderer(colors=enable_colors)
        ])
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(message)s",
        stream=sys.stdout,
    )
    
    # Apply colored formatter for console output if not JSON
    if format_type.lower() != "json" and enable_colors:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(ColoredFormatter("%(levelname)s %(message)s"))
        
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.addHandler(handler)
    
    # Set specific logger levels
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_logger(name: str) -> types.BoundLogger:
    """Get a configured structlog logger instance."""
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> types.BoundLogger:
        """Get logger instance for this class."""
        return structlog.get_logger(self.__class__.__name__)


# Convenience functions for different log levels
def log_error(
    message: str, 
    error: Optional[Exception] = None, 
    **kwargs: Any
) -> None:
    """Log error with optional exception details."""
    logger = structlog.get_logger()
    
    if error:
        kwargs["error_type"] = type(error).__name__
        kwargs["error_message"] = str(error)
    
    logger.error(message, **kwargs)


def log_performance(
    operation: str,
    duration_ms: float,
    **kwargs: Any
) -> None:
    """Log performance metrics."""
    logger = structlog.get_logger()
    logger.info(
        "Performance metric",
        operation=operation,
        duration_ms=duration_ms,
        **kwargs
    )


def log_audit(
    action: str,
    user_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    **kwargs: Any
) -> None:
    """Log audit events."""
    logger = structlog.get_logger()
    logger.info(
        "Audit event",
        action=action,
        user_id=user_id,
        resource_id=resource_id,
        **kwargs
    )