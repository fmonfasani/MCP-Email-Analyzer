    # src/gmail/mapper.py
"""
Gmail API response to EmailData mapping utilities
"""
import base64
import email
from datetime import datetime
from typing import List, Dict, Any, Optional
import structlog

from ..core.interfaces import EmailData, EmailMetadata

logger = structlog.get_logger(__name__)


class GmailMapper:
    """Maps Gmail API responses to EmailData objects"""
    
    @staticmethod
    def map_message_to_email_data(message: Dict[str, Any]) -> EmailData:
        """
        Convert Gmail API message to EmailData
        
        Args:
            message: Gmail API message response
            
        Returns:
            EmailData: Standardized email data
        """
        try:
            headers = GmailMapper._extract_headers(message)
            body_content = GmailMapper._extract_body(message)
            attachments = GmailMapper._extract_attachments(message)
            
            metadata = EmailMetadata(
                thread_id=message.get('threadId'),
                label_ids=message.get('labelIds', []),
                snippet=message.get('snippet', ''),
                size_estimate=message.get('sizeEstimate', 0),
                history_id=message.get('historyId'),
                internal_date=GmailMapper._parse_internal_date(
                    message.get('internalDate')
                )
            )
            
            email_data = EmailData(
                id=message['id'],
                thread_id=message.get('threadId'),
                subject=headers.get('Subject', 'No Subject'),
                sender=headers.get('From', ''),
                recipients=GmailMapper._parse_recipients(headers),
                cc=GmailMapper._parse_cc(headers),
                bcc=GmailMapper._parse_bcc(headers),
                date=GmailMapper._parse_date(headers.get('Date')),
                body=body_content,
                attachments=attachments,
                labels=message.get('labelIds', []),
                is_read='UNREAD' not in message.get('labelIds', []),
                is_starred='STARRED' in message.get('labelIds', []),
                is_important='IMPORTANT' in message.get('labelIds', []),
                metadata=metadata
            )
            
            logger.debug("Mapped Gmail message to EmailData", email_id=email_data.id)
            return email_data
            
        except Exception as e:
            logger.error("Error mapping Gmail message", error=str(e), message_id=message.get('id'))
            raise
    
    @staticmethod
    def _extract_headers(message: Dict[str, Any]) -> Dict[str, str]:
        """Extract headers from Gmail message"""
        headers = {}
        payload = message.get('payload', {})
        
        for header in payload.get('headers', []):
            headers[header['name']] = header['value']
        
        return headers
    
    @staticmethod
    def _extract_body(message: Dict[str, Any]) -> str:
        """Extract body content from Gmail message"""
        payload = message.get('payload', {})
        body = ""
        
        # Handle multipart messages
        if 'parts' in payload:
            for part in payload['parts']:
                body += GmailMapper._extract_part_body(part)
        else:
            body = GmailMapper._extract_part_body(payload)
        
        return body.strip()
    
    @staticmethod
    def _extract_part_body(part: Dict[str, Any]) -> str:
        """Extract body from a message part"""
        mime_type = part.get('mimeType', '')
        
        # Handle nested parts
        if 'parts' in part:
            body = ""
            for nested_part in part['parts']:
                body += GmailMapper._extract_part_body(nested_part)
            return body
        
        # Extract text content
        if mime_type in ['text/plain', 'text/html']:
            body_data = part.get('body', {}).get('data')
            if body_data:
                try:
                    decoded = base64.urlsafe_b64decode(body_data).decode('utf-8')
                    return decoded + "\n"
                except Exception as e:
                    logger.warning("Failed to decode body part", error=str(e))
                    return ""
        
        return ""
    
    @staticmethod
    def _extract_attachments(message: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract attachment information from Gmail message"""
        attachments = []
        payload = message.get('payload', {})
        
        def process_part(part):
            filename = part.get('filename')
            if filename:
                attachment = {
                    'filename': filename,
                    'mime_type': part.get('mimeType'),
                    'size': part.get('body', {}).get('size', 0),
                    'attachment_id': part.get('body', {}).get('attachmentId')
                }
                attachments.append(attachment)
            
            # Process nested parts
            if 'parts' in part:
                for nested_part in part['parts']:
                    process_part(nested_part)
        
        if 'parts' in payload:
            for part in payload['parts']:
                process_part(part)
        
        return attachments
    
    @staticmethod
    def _parse_recipients(headers: Dict[str, str]) -> List[str]:
        """Parse To recipients from headers"""
        to_header = headers.get('To', '')
        if not to_header:
            return []
        
        return [addr.strip() for addr in to_header.split(',') if addr.strip()]
    
    @staticmethod
    def _parse_cc(headers: Dict[str, str]) -> List[str]:
        """Parse CC recipients from headers"""
        cc_header = headers.get('Cc', '')
        if not cc_header:
            return []
        
        return [addr.strip() for addr in cc_header.split(',') if addr.strip()]
    
    @staticmethod
    def _parse_bcc(headers: Dict[str, str]) -> List[str]:
        """Parse BCC recipients from headers"""
        bcc_header = headers.get('Bcc', '')
        if not bcc_header:
            return []
        
        return [addr.strip() for addr in bcc_header.split(',') if addr.strip()]
    
    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        """Parse email date from header"""
        if not date_str:
            return None
        
        try:
            # Parse RFC 2822 date format
            parsed = email.utils.parsedate_tz(date_str)
            if parsed:
                timestamp = email.utils.mktime_tz(parsed)
                return datetime.fromtimestamp(timestamp)
        except Exception as e:
            logger.warning("Failed to parse email date", date_str=date_str, error=str(e))
        
        return None
    
    @staticmethod
    def _parse_internal_date(internal_date: Optional[str]) -> Optional[datetime]:
        """Parse Gmail internal date"""
        if not internal_date:
            return None
        
        try:
            # Internal date is in milliseconds since epoch
            timestamp = int(internal_date) / 1000
            return datetime.fromtimestamp(timestamp)
        except Exception as e:
            logger.warning("Failed to parse internal date", internal_date=internal_date, error=str(e))
        
        return None
    
    @staticmethod
    def map_batch_messages(messages: List[Dict[str, Any]]) -> List[EmailData]:
        """
        Map multiple Gmail messages to EmailData objects
        
        Args:
            messages: List of Gmail API message responses
            
        Returns:
            List of EmailData objects
        """
        email_data_list = []
        
        for message in messages:
            try:
                email_data = GmailMapper.map_message_to_email_data(message)
                email_data_list.append(email_data)
            except Exception as e:
                logger.error(
                    "Failed to map message in batch", 
                    message_id=message.get('id'), 
                    error=str(e)
                )
                continue
        
        logger.info("Mapped batch messages", count=len(email_data_list))
        return email_data_list