"""
Google Drive Service for file operations
"""
import io
from datetime import datetime
from typing import Dict
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError
from config import DRIVE_FOLDER_NAME



class DriveService:
    FOLDER_NAME = DRIVE_FOLDER_NAME
    
    def __init__(self, drive_service):
        self.service = drive_service
        self._ensure_folder_exists()
        
    def _ensure_folder_exists(self):
        """Check if the target folder exists, create it if it doesn't"""
        try:
            # Check if folder exists
            response = self.service.files().list(
                q=f"name='{self.FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            if not response.get('files'):
                # Folder doesn't exist, create it
                folder_metadata = {
                    'name': self.FOLDER_NAME,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                    
                folder = self.service.files().create(
                    body=folder_metadata,
                    fields='id, name'
                ).execute()
                print(f"Created folder: {folder.get('name')} (ID: {folder.get('id')})")
                return folder.get('id')
            else:
                # Folder exists, return its ID
                return response['files'][0]['id']
                
        except Exception as e:
            print(f"Error ensuring folder exists: {e}")
            return None
    
    def upload_file(self, file_data: bytes, original_filename: str, 
                   mime_type: str, invoice_data: Dict) -> str:
        try:
            new_filename = self._generate_filename(original_filename, invoice_data)
            
            media = MediaIoBaseUpload(
                io.BytesIO(file_data),
                mimetype=mime_type,
                resumable=True
            )
            file_metadata = {
                'name': new_filename,
                'parents': [self._ensure_folder_exists()]
            }
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink'
            ).execute()
            
            file_url = file.get('webViewLink', '')
            print(f"Uploaded file: {new_filename}")
            return file_url
            
        except HttpError as error:
            print(f"Error uploading file to Drive: {error}")
            return ""
        except Exception as error:
            print(f"Unexpected error uploading file: {error}")
            return ""
    
    def _generate_filename(self, original_filename: str, invoice_data: Dict) -> str:
        current_date = datetime.now().strftime("%d.%m.%Y")
        
        vendor = invoice_data.get('vendor_name', 'Unknown')
        
        
        invoice_num = invoice_data.get('invoice_number', 'N/A')
        
        
        amount = invoice_data.get('total_amount', 'N/A')
        
        
        file_ext = original_filename.split('.')[-1] if '.' in original_filename else 'bin'
        
        return f"{current_date}_{vendor}_{invoice_num}_{amount}.{file_ext}"
    