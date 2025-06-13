"""
Gmail Service for email operations
"""
import base64
from typing import List, Dict, Optional
from googleapiclient.errors import HttpError
from config import TARGET_SUBJECT, GMAIL_LABEL_NAME

class GmailService:
    def __init__(self, gmail_service):
        self.service = gmail_service
        self.processed_label_id = None
        
    def get_or_create_label(self) -> Optional[str]:
        try:
            labels = self.service.users().labels().list(userId='me').execute()
            for label in labels.get('labels', []):
                if label['name'] == GMAIL_LABEL_NAME:
                    self.processed_label_id = label['id']
                    print(f"Found existing label: {GMAIL_LABEL_NAME}")
                    return label['id']
            
            # Create new label
            label_object = {
                'name': GMAIL_LABEL_NAME,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            
            created_label = self.service.users().labels().create(
                userId='me', body=label_object
            ).execute()
            
            self.processed_label_id = created_label['id']
            print(f"Created new label: {GMAIL_LABEL_NAME}")
            return created_label['id']
            
        except HttpError as error:
            print(f"Error managing Gmail label: {error}")
            return None
    
    def search_target_emails(self) -> List[str]:
        try:
            query = f'subject:{TARGET_SUBJECT} is:unread' # Search for unread emails with the target subject prefix
            results = self.service.users().messages().list(
                userId='me', q=query
            ).execute()
            
            messages = results.get('messages', [])
            message_ids = [msg['id'] for msg in messages]
            print(f"Found {len(message_ids)} unread target emails")
            return message_ids
            
        except HttpError as error:
            print(f"Error searching emails: {error}")
            return []
    
    def get_email_with_attachments(self, message_id: str) -> Dict:
        try:
            message = self.service.users().messages().get(
                userId='me', id=message_id, format='full'
            ).execute()
            
            headers = message['payload'].get('headers', [])
            subject = self._get_header_value(headers, 'Subject')
            
            attachments = []
            self._find_attachments(message['payload'], attachments, message_id)
            
            return {
                'id': message_id,
                'subject': subject,
                'attachments': attachments
            }
            
        except HttpError as error:
            print(f"Error getting email {message_id}: {error}")
            return {}
    
    def download_attachment(self, message_id: str, attachment_id: str) -> bytes:
        try:            
            attachment = self.service.users().messages().attachments().get(
                userId='me', messageId=message_id, id=attachment_id
            ).execute()
            
            return base64.urlsafe_b64decode(attachment['data'])
            
        except HttpError as error:
            print(f"Error downloading attachment: {error}")
            return b''
    
    def mark_as_processed(self, message_id: str):
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute() # Mark as read
            
            if self.processed_label_id:
                self.service.users().messages().modify(
                    userId='me',
                    id=message_id,
                    body={'addLabelIds': [self.processed_label_id]}
                ).execute() # Add processed label
            
            print(f"Marked email {message_id} as processed")
            
        except HttpError as error:
            print(f"Error marking email as processed: {error}")
    
    def _get_header_value(self, headers: List[Dict], name: str) -> str:
        for header in headers:
            if header['name'] == name:
                return header['value']
        return ''
    
    def _find_attachments(self, payload, attachments, message_id):
        if 'parts' in payload:
            for part in payload['parts']:
                self._find_attachments(part, attachments, message_id)
        else:
            if payload.get('filename'):
                attachments.append({
                    'filename': payload['filename'],
                    'mimeType': payload['mimeType'],
                    'attachmentId': payload['body'].get('attachmentId'),
                    'size': payload['body'].get('size', 0)
                })