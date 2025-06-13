"""
Google API Authentication Service
"""
import os
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import SCOPES, CREDENTIALS_FILE, TOKEN_FILE


class AuthService:
    def __init__(self):
        self.credentials = None
        
    def authenticate(self):
        """Authenticate with Google APIs and return credentials"""
        try:
            # Load existing token
            if os.path.exists(TOKEN_FILE):
                self.credentials = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            
            # Refresh or get new credentials
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    if not os.path.exists(CREDENTIALS_FILE):
                        raise FileNotFoundError(f"Credentials file not found: {CREDENTIALS_FILE}")
                    
                    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                    self.credentials = flow.run_local_server(port=0)
                
                # Save credentials
                with open(TOKEN_FILE, 'w') as token:
                    token.write(self.credentials.to_json())
            
            print("Authentication successful")
            return self.credentials
            
        except Exception as e:
            print(f"Authentication failed: {e}")
            raise
    
    def get_gmail_service(self):
        """Get Gmail API service"""
        if not self.credentials:
            self.authenticate()
        return build('gmail', 'v1', credentials=self.credentials)
    
    def get_drive_service(self):
        """Get Drive API service"""
        if not self.credentials:
            self.authenticate()
        return build('drive', 'v3', credentials=self.credentials)
    
    def get_sheets_service(self):
        """Get Sheets API service"""
        if not self.credentials:
            self.authenticate()
        return build('sheets', 'v4', credentials=self.credentials)