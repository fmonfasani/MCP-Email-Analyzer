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

# src/core/interfaces.py
"""
Core interfaces and data models for email operations
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class EmailPriority(Enum):
    """Email priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


@dataclass
class EmailMetadata:
    """Extended email metadata"""
    thread_id: Optional[str] = None
    label_ids: List[str] = None
    snippet: str = ""
    size_estimate: int = 0
    history_id: Optional[str] = None
    internal_date: Optional[datetime] = None
    message_id: Optional[str] = None
    references: List[str] = None
    in_reply_to: Optional[str] = None
    
    def __post_init__(self):
        if self.label_ids is None:
            self.label_ids = []
        if self.references is None:
            self.references = []


@dataclass
class EmailData:
    """Standardized email data structure"""
    id: str
    thread_id: Optional[str]
    subject: str
    sender: str
    recipients: List[str]
    cc: List[str]
    bcc: List[str]
    date: Optional[datetime]
    body: str
    attachments: List[Dict[str, Any]]
    labels: List[str]
    is_read: bool = False
    is_starred: bool = False
    is_important: bool = False
    priority: EmailPriority = EmailPriority.NORMAL
    metadata: Optional[EmailMetadata] = None
    
    def __post_init__(self):
        if not self.recipients:
            self.recipients = []
        if not self.cc:
            self.cc = []
        if not self.bcc:
            self.bcc = []
        if not self.attachments:
            self.attachments = []
        if not self.labels:
            self.labels = []
        if self.metadata is None:
            self.metadata = EmailMetadata()
    
    @property
    def has_attachments(self) -> bool:
        """Check if email has attachments"""
        return len(self.attachments) > 0
    
    @property
    def attachment_count(self) -> int:
        """Get number of attachments"""
        return len(self.attachments)
    
    @property
    def total_recipients(self) -> int:
        """Get total number of recipients (To + CC + BCC)"""
        return len(self.recipients) + len(self.cc) + len(self.bcc)
    
    def get_all_recipients(self) -> List[str]:
        """Get all recipients in a single list"""
        return self.recipients + self.cc + self.bcc
    
    def is_from_sender(self, email_address: str) -> bool:
        """Check if email is from specific sender"""
        return email_address.lower() in self.sender.lower()
    
    def has_label(self, label: str) -> bool:
        """Check if email has specific label"""
        return label in self.labels


@dataclass
class SearchFilters:
    """Email search filters"""
    sender: Optional[str] = None
    recipient: Optional[str] = None
    subject: Optional[str] = None
    body_contains: Optional[str] = None
    has_attachment: Optional[bool] = None
    is_unread: Optional[bool] = None
    is_starred: Optional[bool] = None
    is_important: Optional[bool] = None
    date_after: Optional[datetime] = None
    date_before: Optional[datetime] = None
    labels: List[str] = None
    exclude_labels: List[str] = None
    priority: Optional[EmailPriority] = None
    thread_id: Optional[str] = None
    size_larger_than: Optional[int] = None
    size_smaller_than: Optional[int] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = []
        if self.exclude_labels is None:
            self.exclude_labels = []
    
    def is_empty(self) -> bool:
        """Check if filters are empty"""
        return all([
            not self.sender,
            not self.recipient,
            not self.subject,
            not self.body_contains,
            self.has_attachment is None,
            self.is_unread is None,
            self.is_starred is None,
            self.is_important is None,
            not self.date_after,
            not self.date_before,
            not self.labels,
            not self.exclude_labels,
            self.priority is None,
            not self.thread_id,
            self.size_larger_than is None,
            self.size_smaller_than is None
        ])


@dataclass
class EmailStats:
    """Email statistics"""
    total_emails: int
    unread_emails: int
    starred_emails: int
    important_emails: int
    emails_with_attachments: int
    total_size_bytes: int
    oldest_email_date: Optional[datetime] = None
    newest_email_date: Optional[datetime] = None
    
    @property
    def read_emails(self) -> int:
        """Get number of read emails"""
        return self.total_emails - self.unread_emails
    
    @property
    def read_percentage(self) -> float:
        """Get percentage of read emails"""
        if self.total_emails == 0:
            return 0.0
        return (self.read_emails / self.total_emails) * 100
    
    @property
    def attachment_percentage(self) -> float:
        """Get percentage of emails with attachments"""
        if self.total_emails == 0:
            return 0.0
        return (self.emails_with_attachments / self.total_emails) * 100


class EmailRepository(ABC):
    """Abstract repository for email operations"""
    
    @abstractmethod
    async def get_emails(
        self, 
        limit: int = 10, 
        offset: int = 0,
        filters: Optional[SearchFilters] = None
    ) -> List[EmailData]:
        """
        Retrieve emails with optional filtering and pagination
        
        Args:
            limit: Maximum number of emails to retrieve
            offset: Number of emails to skip
            filters: Optional search filters
            
        Returns:
            List of EmailData objects
        """
        pass
    
    @abstractmethod
    async def get_email_by_id(self, email_id: str) -> EmailData:
        """
        Retrieve a specific email by ID
        
        Args:
            email_id: Unique email identifier
            
        Returns:
            EmailData object
            
        Raises:
            EmailNotFoundError: If email not found
        """
        pass
    
    @abstractmethod
    async def search_emails(self, filters: SearchFilters) -> List[EmailData]:
        """
        Search emails with advanced filters
        
        Args:
            filters: Search criteria
            
        Returns:
            List of matching EmailData objects
        """
        pass
    
    @abstractmethod
    async def mark_as_read(self, email_id: str) -> bool:
        """
        Mark email as read
        
        Args:
            email_id: Email identifier
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def mark_as_unread(self, email_id: str) -> bool:
        """
        Mark email as unread
        
        Args:
            email_id: Email identifier
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def delete_email(self, email_id: str) -> bool:
        """
        Delete email
        
        Args:
            email_id: Email identifier
            
        Returns:
            True if successful
        """
        pass
    
    async def mark_multiple_as_read(self, email_ids: List[str]) -> List[str]:
        """
        Mark multiple emails as read
        
        Args:
            email_ids: List of email identifiers
            
        Returns:
            List of successfully processed email IDs
        """
        successful_ids = []
        for email_id in email_ids:
            try:
                if await self.mark_as_read(email_id):
                    successful_ids.append(email_id)
            except Exception:
                continue  # Skip failed operations
        return successful_ids
    
    async def mark_multiple_as_unread(self, email_ids: List[str]) -> List[str]:
        """
        Mark multiple emails as unread
        
        Args:
            email_ids: List of email identifiers
            
        Returns:
            List of successfully processed email IDs
        """
        successful_ids = []
        for email_id in email_ids:
            try:
                if await self.mark_as_unread(email_id):
                    successful_ids.append(email_id)
            except Exception:
                continue  # Skip failed operations
        return successful_ids
    
    async def delete_multiple_emails(self, email_ids: List[str]) -> List[str]:
        """
        Delete multiple emails
        
        Args:
            email_ids: List of email identifiers
            
        Returns:
            List of successfully deleted email IDs
        """
        successful_ids = []
        for email_id in email_ids:
            try:
                if await self.delete_email(email_id):
                    successful_ids.append(email_id)
            except Exception:
                continue  # Skip failed operations
        return successful_ids
    
    async def get_email_stats(self, filters: Optional[SearchFilters] = None) -> EmailStats:
        """
        Get email statistics
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            EmailStats object
        """
        emails = await self.search_emails(filters) if filters else await self.get_emails(limit=1000)
        
        total_emails = len(emails)
        unread_emails = sum(1 for email in emails if not email.is_read)
        starred_emails = sum(1 for email in emails if email.is_starred)
        important_emails = sum(1 for email in emails if email.is_important)
        emails_with_attachments = sum(1 for email in emails if email.has_attachments)
        
        # Calculate total size (estimate based on metadata)
        total_size_bytes = sum(
            email.metadata.size_estimate if email.metadata and email.metadata.size_estimate else 0
            for email in emails
        )
        
        # Find date range
        dates = [email.date for email in emails if email.date]
        oldest_date = min(dates) if dates else None
        newest_date = max(dates) if dates else None
        
        return EmailStats(
            total_emails=total_emails,
            unread_emails=unread_emails,
            starred_emails=starred_emails,
            important_emails=important_emails,
            emails_with_attachments=emails_with_attachments,
            total_size_bytes=total_size_bytes,
            oldest_email_date=oldest_date,
            newest_email_date=newest_date
        )
    
    async def health_check(self) -> bool:
        """
        Check if the email service is healthy
        
        Returns:
            True if service is accessible
        """
        try:
            # Try to fetch a small number of emails
            await self.get_emails(limit=1)
            return True
        except Exception:
            return False


class EmailAnalyzer(ABC):
    """Abstract analyzer for email analysis"""
    
    @abstractmethod
    async def analyze_email(self, email: EmailData) -> Dict[str, Any]:
        """
        Analyze a single email
        
        Args:
            email: EmailData object
            
        Returns:
            Analysis results
        """
        pass
    
    @abstractmethod
    async def analyze_emails_batch(self, emails: List[EmailData]) -> List[Dict[str, Any]]:
        """
        Analyze multiple emails in batch
        
        Args:
            emails: List of EmailData objects
            
        Returns:
            List of analysis results
        """
        pass
    
    @abstractmethod
    async def get_insights(self, emails: List[EmailData]) -> Dict[str, Any]:
        """
        Get insights from email collection
            
        Args:
            emails: List of EmailData objects
            
        Returns:
            Insights and patterns
        """
        pass