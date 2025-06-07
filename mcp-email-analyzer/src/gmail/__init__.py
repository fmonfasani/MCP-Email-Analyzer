
"""Gmail integration package for MCP Email Analyzer
"""
from .client import GmailRepository
from .auth import GmailAuthenticator
from .mapper import GmailMapper

__all__ = [
    'GmailRepository',
    'GmailAuthenticator', 
    'GmailMapper'
]

__version__ = '1.0.0'