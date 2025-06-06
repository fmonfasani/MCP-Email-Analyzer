# src/gmail/client.py
"""
Gmail Repository implementation using Gmail API
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from googleapiclient.errors import HttpError
from cachetools import TTLCache

from ..core.interfaces import EmailRepository, EmailData, SearchFilters
from ..server.config import GmailSettings
from ..server.exceptions import EmailNotFoundError, EmailServiceError, RateLimitError
from .auth import GmailAuthenticator
from .mapper import GmailMapper

logger = structlog.get_logger(__name__)


class GmailRepository(EmailRepository):
    """Gmail API implementation of EmailRepository"""
    
    def __init__(self, settings: GmailSettings):
        self.settings = settings
        self.authenticator = GmailAuthenticator(settings)
        self.mapper = GmailMapper()
        self._service = None
        
        # TTL Cache for recent emails
        self._cache = TTLCache(maxsize=1000, ttl=settings.cache_ttl)
        
    async def _get_service(self):
        """Get authenticated Gmail service with lazy initialization"""
        if not self._service:
            self._service = await self.authenticator.get_service()
        return self._service
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((HttpError, RateLimitError))
    )
    async def get_emails(
        self, 
        limit: int = 10, 
        offset: int = 0,
        filters: Optional[SearchFilters] = None
    ) -> List[EmailData]:
        """
        Retrieve emails with optional filtering
        
        Args:
            limit: Maximum number of emails to retrieve
            offset: Number of emails to skip
            filters: Optional search filters
            
        Returns:
            List of EmailData objects
            
        Raises:
            EmailServiceError: If API call fails
        """
        try:
            logger.info("Fetching emails", limit=limit, offset=offset)
            service = await self._get_service()
            
            # Build query string
            query = self._build_query(filters) if filters else ""
            
            # Get message list
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=min(limit, self.settings.max_results),
                pageToken=None  # Handle pagination if needed
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                logger.info("No messages found")
                return []
            
            # Apply offset
            if offset > 0:
                messages = messages[offset:]
            
            # Batch fetch message details
            email_data_list = await self._fetch_messages_batch(messages[:limit])
            
            logger.info("Successfully fetched emails", count=len(email_data_list))
            return email_data_list
            
        except HttpError as e:
            if e.resp.status == 429:
                logger.warning("Rate limit exceeded")
                raise RateLimitError("Gmail API rate limit exceeded")
            
            logger.error("Gmail API error", error=str(e), status=e.resp.status)
            raise EmailServiceError(f"Gmail API error: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error fetching emails", error=str(e))
            raise EmailServiceError(f"Failed to fetch emails: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((HttpError, RateLimitError))
    )
    async def get_email_by_id(self, email_id: str) -> EmailData:
        """
        Retrieve a specific email by ID
        
        Args:
            email_id: Gmail message ID
            
        Returns:
            EmailData object
            
        Raises:
            EmailNotFoundError: If email not found
            EmailServiceError: If API call fails
        """
        # Check cache first
        if email_id in self._cache:
            logger.debug("Email found in cache", email_id=email_id)
            return self._cache[email_id]
        
        try:
            logger.info("Fetching email by ID", email_id=email_id)
            service = await self._get_service()
            
            message = service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()
            
            email_data = self.mapper.map_message_to_email_data(message)
            
            # Cache the result
            self._cache[email_id] = email_data
            
            logger.info("Successfully fetched email", email_id=email_id)
            return email_data
            
        except HttpError as e:
            if e.resp.status == 404:
                logger.warning("Email not found", email_id=email_id)
                raise EmailNotFoundError(f"Email not found: {email_id}")
            elif e.resp.status == 429:
                logger.warning("Rate limit exceeded")
                raise RateLimitError("Gmail API rate limit exceeded")
            
            logger.error("Gmail API error", error=str(e), email_id=email_id)
            raise EmailServiceError(f"Gmail API error: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error fetching email", error=str(e), email_id=email_id)
            raise EmailServiceError(f"Failed to fetch email: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((HttpError, RateLimitError))
    )
    async def search_emails(self, filters: SearchFilters) -> List[EmailData]:
        """
        Search emails with advanced filters
        
        Args:
            filters: Search filters
            
        Returns:
            List of matching EmailData objects
        """
        try:
            logger.info("Searching emails with filters")
            service = await self._get_service()
            
            query = self._build_query(filters)
            logger.debug("Search query", query=query)
            
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=self.settings.max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                logger.info("No messages found for search")
                return []
            
            # Batch fetch message details
            email_data_list = await self._fetch_messages_batch(messages)
            
            logger.info("Search completed", found_count=len(email_data_list))
            return email_data_list
            
        except HttpError as e:
            if e.resp.status == 429:
                raise RateLimitError("Gmail API rate limit exceeded")
            raise EmailServiceError(f"Gmail search error: {str(e)}")
        except Exception as e:
            logger.error("Search error", error=str(e))
            raise EmailServiceError(f"Search failed: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((HttpError, RateLimitError))
    )
    async def mark_as_read(self, email_id: str) -> bool:
        """
        Mark email as read
        
        Args:
            email_id: Gmail message ID
            
        Returns:
            True if successful
        """
        try:
            logger.info("Marking email as read", email_id=email_id)
            service = await self._get_service()
            
            service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            # Update cache if present
            if email_id in self._cache:
                self._cache[email_id].is_read = True
            
            logger.info("Email marked as read", email_id=email_id)
            return True
            
        except HttpError as e:
            if e.resp.status == 404:
                raise EmailNotFoundError(f"Email not found: {email_id}")
            elif e.resp.status == 429:
                raise RateLimitError("Gmail API rate limit exceeded")
            
            logger.error("Error marking email as read", error=str(e), email_id=email_id)
            raise EmailServiceError(f"Failed to mark as read: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error marking as read", error=str(e), email_id=email_id)
            raise EmailServiceError(f"Failed to mark as read: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((HttpError, RateLimitError))
    )
    async def mark_as_unread(self, email_id: str) -> bool:
        """
        Mark email as unread
        
        Args:
            email_id: Gmail message ID
            
        Returns:
            True if successful
        """
        try:
            logger.info("Marking email as unread", email_id=email_id)
            service = await self._get_service()
            
            service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'addLabelIds': ['UNREAD']}
            ).execute()
            
            # Update cache if present
            if email_id in self._cache:
                self._cache[email_id].is_read = False
            
            logger.info("Email marked as unread", email_id=email_id)
            return True
            
        except HttpError as e:
            if e.resp.status == 404:
                raise EmailNotFoundError(f"Email not found: {email_id}")
            elif e.resp.status == 429:
                raise RateLimitError("Gmail API rate limit exceeded")
            
            logger.error("Error marking email as unread", error=str(e), email_id=email_id)
            raise EmailServiceError(f"Failed to mark as unread: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error marking as unread", error=str(e), email_id=email_id)
            raise EmailServiceError(f"Failed to mark as unread: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((HttpError, RateLimitError))
    )
    async def delete_email(self, email_id: str) -> bool:
        """
        Delete email (move to trash)
        
        Args:
            email_id: Gmail message ID
            
        Returns:
            True if successful
        """
        try:
            logger.info("Deleting email", email_id=email_id)
            service = await self._get_service()
            
            service.users().messages().trash(
                userId='me',
                id=email_id
            ).execute()
            
            # Remove from cache
            self._cache.pop(email_id, None)
            
            logger.info("Email deleted", email_id=email_id)
            return True
            
        except HttpError as e:
            if e.resp.status == 404:
                raise EmailNotFoundError(f"Email not found: {email_id}")
            elif e.resp.status == 429:
                raise RateLimitError("Gmail API rate limit exceeded")
            
            logger.error("Error deleting email", error=str(e), email_id=email_id)
            raise EmailServiceError(f"Failed to delete email: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error deleting email", error=str(e), email_id=email_id)
            raise EmailServiceError(f"Failed to delete email: {str(e)}")
    
    async def _fetch_messages_batch(self, messages: List[Dict[str, Any]]) -> List[EmailData]:
        """
        Fetch multiple messages in batch with concurrent processing
        
        Args:
            messages: List of message objects with 'id' field
            
        Returns:
            List of EmailData objects
        """
        async def fetch_single_message(message_info: Dict[str, Any]) -> Optional[EmailData]:
            """Fetch a single message"""
            try:
                message_id = message_info['id']
                
                # Check cache first
                if message_id in self._cache:
                    return self._cache[message_id]
                
                service = await self._get_service()
                message = service.users().messages().get(
                    userId='me',
                    id=message_id,
                    format='full'
                ).execute()
                
                email_data = self.mapper.map_message_to_email_data(message)
                
                # Cache the result
                self._cache[message_id] = email_data
                
                return email_data
                
            except Exception as e:
                logger.error("Error fetching message in batch", 
                           message_id=message_info.get('id'), error=str(e))
                return None
        
        # Process messages concurrently with controlled concurrency
        semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
        
        async def fetch_with_semaphore(message_info):
            async with semaphore:
                return await fetch_single_message(message_info)
        
        tasks = [fetch_with_semaphore(msg) for msg in messages]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None results and exceptions
        email_data_list = [
            result for result in results 
            if result is not None and not isinstance(result, Exception)
        ]
        
        return email_data_list
    
    def _build_query(self, filters: SearchFilters) -> str:
        """
        Build Gmail search query from filters
        
        Args:
            filters: Search filters
            
        Returns:
            Gmail search query string
        """
        query_parts = []
        
        if filters.sender:
            query_parts.append(f"from:{filters.sender}")
        
        if filters.recipient:
            query_parts.append(f"to:{filters.recipient}")
        
        if filters.subject:
            query_parts.append(f"subject:{filters.subject}")
        
        if filters.body_contains:
            query_parts.append(f"{filters.body_contains}")
        
        if filters.has_attachment is not None:
            if filters.has_attachment:
                query_parts.append("has:attachment")
            else:
                query_parts.append("-has:attachment")
        
        if filters.is_unread is not None:
            if filters.is_unread:
                query_parts.append("is:unread")
            else:
                query_parts.append("is:read")
        
        if filters.date_after:
            date_str = filters.date_after.strftime("%Y/%m/%d")
            query_parts.append(f"after:{date_str}")
        
        if filters.date_before:
            date_str = filters.date_before.strftime("%Y/%m/%d")
            query_parts.append(f"before:{date_str}")
        
        if filters.labels:
            for label in filters.labels:
                query_parts.append(f"label:{label}")
        
        query = " ".join(query_parts)
        logger.debug("Built search query", query=query)
        
        return query
    
    async def get_unread_count(self) -> int:
        """
        Get count of unread emails
        
        Returns:
            Number of unread emails
        """
        try:
            service = await self._get_service()
            
            results = service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=1
            ).execute()
            
            # Gmail returns estimated result count
            return results.get('resultSizeEstimate', 0)
            
        except Exception as e:
            logger.error("Error getting unread count", error=str(e))
            raise EmailServiceError(f"Failed to get unread count: {str(e)}")
    
    async def health_check(self) -> bool:
        """
        Check if Gmail service is accessible
        
        Returns:
            True if service is healthy
        """
        try:
            service = await self._get_service()
            
            # Simple API call to check connectivity
            service.users().getProfile(userId='me').execute()
            
            logger.info("Gmail service health check passed")
            return True
            
        except Exception as e:
            logger.error("Gmail service health check failed", error=str(e))
            return False