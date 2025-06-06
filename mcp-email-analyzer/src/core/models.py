"""Data models for MCP Email Analyzer."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class EmailData:
    """Email data model with all necessary fields."""
    id: str
    subject: str
    sender: str
    content: str
    timestamp: str
    labels: List[str] = field(default_factory=list)
    
    # Extended fields for rich email data
    recipient: Optional[str] = None
    cc: List[str] = field(default_factory=list)
    bcc: List[str] = field(default_factory=list)
    thread_id: Optional[str] = None
    message_id: Optional[str] = None
    in_reply_to: Optional[str] = None
    has_attachments: bool = False
    is_read: bool = False
    is_starred: bool = False
    is_important: bool = False
    snippet: Optional[str] = None
    raw_headers: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate email data after initialization."""
        if not self.id:
            raise ValueError("Email ID cannot be empty")
        if not self.sender:
            raise ValueError("Email sender cannot be empty")


@dataclass 
class AnalysisResult:
    """Email analysis result model."""
    email_id: str
    sentiment: str  # positive, negative, neutral
    priority: str   # high, medium, low
    category: str
    confidence: float
    summary: str
    
    # Extended analysis fields
    keywords: List[str] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    language: Optional[str] = None
    reading_time_minutes: Optional[int] = None
    complexity_score: Optional[float] = None
    action_required: bool = False
    deadline_detected: Optional[str] = None
    sentiment_scores: Dict[str, float] = field(default_factory=dict)
    analysis_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def __post_init__(self):
        """Validate analysis result after initialization."""
        if not self.email_id:
            raise ValueError("Email ID cannot be empty")
        
        if self.sentiment not in ["positive", "negative", "neutral"]:
            raise ValueError("Sentiment must be 'positive', 'negative', or 'neutral'")
        
        if self.priority not in ["high", "medium", "low"]:
            raise ValueError("Priority must be 'high', 'medium', or 'low'")
        
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


@dataclass
class EmailQuery:
    """Email query parameters model."""
    query_string: str = ""
    limit: int = 50
    offset: int = 0
    include_spam_trash: bool = False
    label_ids: List[str] = field(default_factory=list)
    after_date: Optional[str] = None
    before_date: Optional[str] = None
    has_attachment: Optional[bool] = None
    is_unread: Optional[bool] = None
    from_sender: Optional[str] = None
    to_recipient: Optional[str] = None
    subject_contains: Optional[str] = None
    
    def build_gmail_query(self) -> str:
        """Build Gmail API query string from parameters."""
        query_parts = []
        
        if self.query_string:
            query_parts.append(self.query_string)
        
        if self.from_sender:
            query_parts.append(f"from:{self.from_sender}")
        
        if self.to_recipient:
            query_parts.append(f"to:{self.to_recipient}")
        
        if self.subject_contains:
            query_parts.append(f"subject:{self.subject_contains}")
        
        if self.after_date:
            query_parts.append(f"after:{self.after_date}")
        
        if self.before_date:
            query_parts.append(f"before:{self.before_date}")
        
        if self.has_attachment is not None:
            query_parts.append("has:attachment" if self.has_attachment else "-has:attachment")
        
        if self.is_unread is not None:
            query_parts.append("is:unread" if self.is_unread else "-is:unread")
        
        if not self.include_spam_trash:
            query_parts.append("-in:spam -in:trash")
        
        return " ".join(query_parts)


@dataclass
class EmailAction:
    """Email action model for batch operations."""
    action_type: str  # mark_read, mark_unread, star, unstar, archive, delete, add_label, remove_label
    email_ids: List[str]
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate email action after initialization."""
        valid_actions = {
            "mark_read", "mark_unread", "star", "unstar", 
            "archive", "delete", "add_label", "remove_label",
            "move_to_trash", "remove_from_trash"
        }
        
        if self.action_type not in valid_actions:
            raise ValueError(f"Invalid action type: {self.action_type}")
        
        if not self.email_ids:
            raise ValueError("Email IDs list cannot be empty")