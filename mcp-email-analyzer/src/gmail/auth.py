# src/gmail/auth.py
"""
Gmail OAuth2 Authentication handler
"""
import json
import os
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import structlog

from ..server.config import GmailSettings
from ..server.exceptions import AuthenticationError

logger = structlog.get_logger(__name__)


class GmailAuthenticator:
    """Handles Gmail OAuth2 authentication flow"""
    
    def __init__(self, settings: GmailSettings):
        self.settings = settings
        self.creds: Optional[Credentials] = None
        self._service = None
    
    async def authenticate(self) -> Credentials:
        """
        Authenticate with Gmail API using OAuth2 flow
        
        Returns:
            Credentials: Valid OAuth2 credentials
            
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            logger.info("Starting Gmail authentication")
            
            # Load existing credentials if available
            if os.path.exists(self.settings.token_path):
                self.creds = Credentials.from_authorized_user_file(
                    self.settings.token_path, self.settings.scopes
                )
                logger.info("Loaded existing credentials")
            
            # If there are no (valid) credentials available, let the user log in
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    logger.info("Refreshing expired credentials")
                    self.creds.refresh(Request())
                else:
                    logger.info("Starting OAuth2 flow")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.settings.credentials_path, self.settings.scopes
                    )
                    self.creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(self.settings.token_path, 'w') as token:
                    token.write(self.creds.to_json())
                    logger.info("Saved new credentials")
            
            logger.info("Gmail authentication successful")
            return self.creds
            
        except Exception as e:
            logger.error("Gmail authentication failed", error=str(e))
            raise AuthenticationError(f"Gmail authentication failed: {str(e)}")
    
    async def get_service(self):
        """
        Get authenticated Gmail service instance
        
        Returns:
            Gmail service instance
        """
        if not self._service:
            if not self.creds:
                await self.authenticate()
            
            self._service = build('gmail', 'v1', credentials=self.creds)
            logger.info("Gmail service initialized")
        
        return self._service
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated with valid credentials"""
        return self.creds is not None and self.creds.valid
    
    async def revoke_credentials(self):
        """Revoke current credentials and remove token file"""
        try:
            if self.creds:
                self.creds.revoke(Request())
                logger.info("Credentials revoked")
            
            if os.path.exists(self.settings.token_path):
                os.remove(self.settings.token_path)
                logger.info("Token file removed")
            
            self.creds = None
            self._service = None
            
        except Exception as e:
            logger.error("Error revoking credentials", error=str(e))
            raise AuthenticationError(f"Failed to revoke credentials: {str(e)}")