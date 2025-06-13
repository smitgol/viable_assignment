"""
Main application for Gmail invoice processing automation
"""
import schedule
import time
from typing import List

# Import our services
from services.auth_service import AuthService
from services.gmail_service import GmailService
from services.drive_service import DriveService
from services.sheets_service import SheetsService
from services.invoice_extractor import ExtractionService
from config import SUPPORTED_MIME_TYPES, SCHEDULE_HOURS

class InvoiceProcessor:
    def __init__(self):
        self.auth_service = AuthService()
        self.gmail_service = None
        self.drive_service = None
        self.sheets_service = None
        self.extraction_service = ExtractionService()
        
    def initialize_services(self):
        """Initialize all Google API services"""
        try:
            print("Initializing services...")
            
            # Authenticate
            self.auth_service.authenticate()
            
            # Initialize services
            gmail_api = self.auth_service.get_gmail_service()
            drive_api = self.auth_service.get_drive_service()
            sheets_api = self.auth_service.get_sheets_service()
            
            self.gmail_service = GmailService(gmail_api)
            self.drive_service = DriveService(drive_api)
            self.sheets_service = SheetsService(sheets_api)
            
            # Setup Gmail label
            self.gmail_service.get_or_create_label()
            
            print("Services initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize services: {e}")
            raise
    
    def process_emails(self):
        """Main processing function"""
        try:
            print("Starting email processing...")
            
            if not self.gmail_service:
                self.initialize_services()
            
            # Get target emails
            email_ids = self.gmail_service.search_target_emails()
            
            if not email_ids:
                print("No unread target emails found")
                return
            
            processed_count = 0
            
            for email_id in email_ids:
                try:
                    processed_count += self._process_single_email(email_id)
                except Exception as e:
                    print(f"Error processing email {email_id}: {e}")
                    continue
            
            print(f"Processing complete. Processed {processed_count} attachments")
            
        except Exception as e:
            print(f"Error in main processing: {e}")
    
    def _process_single_email(self, email_id: str) -> int:
        processed_count = 0
        
        email_data = self.gmail_service.get_email_with_attachments(email_id)
        
        if not email_data or not email_data.get('attachments'):
            return 0
        
        for attachment in email_data['attachments']:
            if self._process_attachment(email_id, attachment):
                processed_count += 1
        
        # Mark email as processed if we processed any attachments
        if processed_count > 0:
            self.gmail_service.mark_as_processed(email_id)
        
        return processed_count
    
    def _process_attachment(self, email_id: str, attachment: dict) -> bool:
        """Process a single attachment"""
        try:
            # Check if file type is supported
            if attachment['mimeType'] not in SUPPORTED_MIME_TYPES:
                return False
            
            file_data = self.gmail_service.download_attachment(
                email_id, attachment['attachmentId']
            )
            
            if not file_data:
                return False
            
            invoice_data = self.extraction_service.extract_invoice_data(
                file_data, attachment['filename'], attachment['mimeType']
            )
            
            file_url = self.drive_service.upload_file(
                file_data, attachment['filename'], 
                attachment['mimeType'], invoice_data
            )
            
            if not file_url:
                return False
            
            success = self.sheets_service.log_processed_data(
                invoice_data, file_url, attachment['mimeType']
            )
            
            if success:
                print(f"Successfully processed: {attachment['filename']}")
                return True
            else:
                print(f"Failed to log data for: {attachment['filename']}")
                return False
                
        except Exception as e:
            print(f"Error processing attachment {attachment['filename']}: {e}")
            return False

def run_once():
    """Run the processor once"""
    processor = InvoiceProcessor()
    processor.process_emails()

def run_scheduled():
    """Run with scheduler"""
    processor = InvoiceProcessor()
    
    # Schedule the job
    schedule.every(SCHEDULE_HOURS).hours.do(processor.process_emails)
    
    print(f"Scheduler started. Running every {SCHEDULE_HOURS} hours...")
    
    # Run once immediately
    processor.process_emails()
    
    # Keep scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    #run_once()
    run_scheduled()