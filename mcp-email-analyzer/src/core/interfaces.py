"""Interfaces and protocols for MCP Email Analyzer."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .models import EmailData, AnalysisResult, EmailQuery, EmailAction


# Original required interfaces (exact implementation)
@dataclass
class EmailData:
    id: str
    subject: str
    sender: str
    content: str
    timestamp: str
    labels: List[str]


@dataclass
class AnalysisResult:
    email_id: str
    sentiment: str  # positive, negative, neutral
    priority: str   # high, medium, low
    category: str
    confidence: float
    summary: str


class EmailRepository(ABC):
    """Abstract repository for email data access."""
    
    @abstractmethod
    async def get_email(self, email_id: str) -> EmailData:
        """Get a single email by ID."""
        pass
    
    @abstractmethod
    async def list_emails(self, query: str, limit: int) -> List[EmailData]:
        """List emails based on query and limit."""
        pass
    
    @abstractmethod
    async def update_email(self, email_id: str, actions: Dict[str, Any]) -> bool:
        """Update email with specified actions."""
        pass


class EmailAnalyzer(ABC):
    """Abstract email analyzer interface."""
    
    @abstractmethod
    async def analyze_email(self, email: EmailData) -> AnalysisResult:
        """Analyze email and return analysis result."""
        pass


# Extended interfaces for full functionality
class ExtendedEmailRepository(EmailRepository):
    """Extended email repository with additional methods."""
    
    @abstractmethod
    async def search_emails(self, query: EmailQuery) -> List[EmailData]:
        """Search emails with advanced query parameters."""
        pass
    
    @abstractmethod
    async def batch_update_emails(self, actions: List[EmailAction]) -> Dict[str, bool]:
        """Perform batch operations on multiple emails."""
        pass
    
    @abstractmethod
    async def get_email_thread(self, thread_id: str) -> List[EmailData]:
        """Get all emails in a thread."""
        pass
    
    @abstractmethod
    async def get_labels(self) -> List[Dict[str, str]]:
        """Get available email labels."""
        pass
    
    @abstractmethod
    async def create_label(self, name: str, visibility: str = "labelShow") -> str:
        """Create a new label and return its ID."""
        pass


class ExtendedEmailAnalyzer(EmailAnalyzer):
    """Extended email analyzer with additional capabilities."""
    
    @abstractmethod
    async def batch_analyze_emails(self, emails: List[EmailData]) -> List[AnalysisResult]:
        """Analyze multiple emails in batch."""
        pass
    
    @abstractmethod
    async def analyze_thread(self, emails: List[EmailData]) -> Dict[str, Any]:
        """Analyze email thread conversation."""
        pass
    
    @abstractmethod
    async def extract_action_items(self, email: EmailData) -> List[Dict[str, Any]]:
        """Extract action items from email content."""
        pass
    
    @abstractmethod
    async def detect_urgency(self, email: EmailData) -> Dict[str, Any]:
        """Detect urgency indicators in email."""
        pass


class AnalyticsProvider(ABC):
    """Interface for email analytics and reporting."""
    
    @abstractmethod
    async def get_email_stats(self, date_range: Dict[str, str]) -> Dict[str, Any]:
        """Get email statistics for date range."""
        pass
    
    @abstractmethod
    async def get_sender_analysis(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top senders analysis."""
        pass
    
    @abstractmethod
    async def get_category_distribution(self) -> Dict[str, int]:
        """Get email category distribution."""
        pass
    
    @abstractmethod
    async def get_sentiment_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get sentiment trends over time."""
        pass


class NotificationProvider(ABC):
    """Interface for email notifications and alerts."""
    
    @abstractmethod
    async def send_alert(self, email_id: str, alert_type: str, message: str) -> bool:
        """Send alert for specific email."""
        pass
    
    @abstractmethod
    async def configure_rules(self, rules: List[Dict[str, Any]]) -> bool:
        """Configure notification rules."""
        pass
    
    @abstractmethod
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get current active alerts."""
        pass

