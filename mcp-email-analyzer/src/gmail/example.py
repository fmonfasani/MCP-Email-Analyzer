# example_usage.py
"""
Example usage of Gmail integration
"""
import asyncio
from datetime import datetime, timedelta
import structlog

from src.server.config import GmailSettings
from src.core.interfaces import SearchFilters, EmailPriority
from src.gmail.factory import create_gmail_repository
from src.server.exceptions import EmailNotFoundError, RateLimitError

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


async def main():
    """Example usage of Gmail integration"""
    
    # Configure Gmail settings
    gmail_settings = GmailSettings(
        credentials_path="path/to/credentials.json",
        token_path="path/to/token.json",
        scopes=["https://www.googleapis.com/auth/gmail.modify"],
        max_results=50,
        cache_ttl=300,
        batch_size=10
    )
    
    # Create repository
    repo = create_gmail_repository(gmail_settings)
    
    try:
        # Health check
        logger.info("Performing health check...")
        is_healthy = await repo.health_check()
        logger.info("Health check result", healthy=is_healthy)
        
        if not is_healthy:
            logger.error("Gmail service is not healthy")
            return
        
        # Get recent emails
        logger.info("Fetching recent emails...")
        recent_emails = await repo.get_emails(limit=10)
        logger.info("Fetched emails", count=len(recent_emails))
        
        for email in recent_emails[:3]:  # Show first 3
            print(f"\nEmail ID: {email.id}")
            print(f"Subject: {email.subject}")
            print(f"From: {email.sender}")
            print(f"Date: {email.date}")
            print(f"Read: {email.is_read}")
            print(f"Attachments: {email.attachment_count}")
            print(f"Labels: {', '.join(email.labels)}")
            print("-" * 50)
        
        # Search for unread emails
        logger.info("Searching for unread emails...")
        unread_filters = SearchFilters(is_unread=True)
        unread_emails = await repo.search_emails(unread_filters)
        logger.info("Found unread emails", count=len(unread_emails))
        
        # Search for emails with attachments from last week
        logger.info("Searching for emails with attachments from last week...")
        week_ago = datetime.now() - timedelta(days=7)
        attachment_filters = SearchFilters(
            has_attachment=True,
            date_after=week_ago
        )
        attachment_emails = await repo.search_emails(attachment_filters)
        logger.info("Found emails with attachments", count=len(attachment_emails))
        
        # Search for emails from specific sender
        logger.info("Searching for emails from specific sender...")
        sender_filters = SearchFilters(sender="example@gmail.com")
        sender_emails = await repo.search_emails(sender_filters)
        logger.info("Found emails from sender", count=len(sender_emails))
        
        # Get email statistics
        logger.info("Getting email statistics...")
        stats = await repo.get_email_stats()
        print(f"\n=== Email Statistics ===")
        print(f"Total emails: {stats.total_emails}")
        print(f"Unread emails: {stats.unread_emails}")
        print(f"Read percentage: {stats.read_percentage:.1f}%")
        print(f"Starred emails: {stats.starred_emails}")
        print(f"Important emails: {stats.important_emails}")
        print(f"Emails with attachments: {stats.emails_with_attachments}")
        print(f"Attachment percentage: {stats.attachment_percentage:.1f}%")
        print(f"Total size: {stats.total_size_bytes / 1024 / 1024:.1f} MB")
        print(f"Oldest email: {stats.oldest_email_date}")
        print(f"Newest email: {stats.newest_email_date}")
        
        # Demonstrate email operations
        if recent_emails:
            first_email = recent_emails[0]
            
            # Get specific email by ID
            logger.info("Fetching email by ID...")
            email_detail = await repo.get_email_by_id(first_email.id)
            print(f"\nDetailed email:")
            print(f"Subject: {email_detail.subject}")
            print(f"Body preview: {email_detail.body[:200]}...")
            
            # Mark as read/unread operations
            if not first_email.is_read:
                logger.info("Marking email as read...")
                await repo.mark_as_read(first_email.id)
                logger.info("Email marked as read")
            else:
                logger.info("Marking email as unread...")
                await repo.mark_as_unread(first_email.id)
                logger.info("Email marked as unread")
        
        # Batch operations example
        if len(recent_emails) > 1:
            email_ids = [email.id for email in recent_emails[:3]]
            
            logger.info("Performing batch mark as read...")
            successful_ids = await repo.mark_multiple_as_read(email_ids)
            logger.info("Batch operation completed", successful_count=len(successful_ids))
        
        # Advanced search example
        logger.info("Performing advanced search...")
        advanced_filters = SearchFilters(
            subject="meeting",
            date_after=datetime.now() - timedelta(days=30),
            has_attachment=False,
            is_unread=False
        )
        advanced_results = await repo.search_emails(advanced_filters)
        logger.info("Advanced search completed", count=len(advanced_results))
        
        logger.info("Gmail integration example completed successfully")
        
    except EmailNotFoundError as e:
        logger.error("Email not found", error=str(e))
    except RateLimitError as e:
        logger.error("Rate limit exceeded", error=str(e))
    except Exception as e:
        logger.error("Unexpected error", error=str(e))
        raise


async def demonstrate_error_handling():
    """Demonstrate error handling"""
    
    gmail_settings = GmailSettings(
        credentials_path="credentials.json",
        token_path="token.json"
    )
    
    repo = create_gmail_repository(gmail_settings)
    
    try:
        # Try to get non-existent email
        await repo.get_email_by_id("non_existent_id")
    except EmailNotFoundError:
        logger.info("Handled EmailNotFoundError correctly")
    
    try:
        # Try operations that might hit rate limits
        for i in range(100):
            await repo.get_emails(limit=1)
    except RateLimitError:
        logger.info("Handled RateLimitError correctly")


if __name__ == "__main__":
    print("=== Gmail Integration Example ===")
    asyncio.run(main())
    
    print("\n=== Error Handling Example ===")
    asyncio.run(demonstrate_error_handling())