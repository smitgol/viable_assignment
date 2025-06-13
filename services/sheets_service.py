"""
Google Sheets Service for logging data
"""
import logging
from datetime import datetime
from typing import Dict
from googleapiclient.errors import HttpError
from config import SPREADSHEET_ID


class SheetsService:
    def __init__(self, sheets_service):
        self.service = sheets_service
        self.setup_headers()
    
    def log_processed_data(self, invoice_data: Dict, file_url: str, file_type: str):
        """Log processed invoice data to Google Sheets"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Prepare row data matching the required columns
            row_data = [
                timestamp,
                invoice_data.get('invoice_date', 'N/A'),
                invoice_data.get('invoice_number', 'N/A'),
                invoice_data.get('total_amount', 'N/A'),
                invoice_data.get('vendor_name', 'N/A'),
                file_url,
                file_type
            ]
            
            # Append to sheet
            body = {'values': [row_data]}
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range='A:G',  # Columns A through G
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"Logged data for vendor: {invoice_data.get('vendor_name', 'Unknown')}")
            return True
            
        except HttpError as error:
            print(f"Error logging to sheets: {error}")
            return False
        except Exception as error:
            print(f"Unexpected error logging to sheets: {error}")
            return False
    
    def setup_headers(self):
        try:
            # Check if header already exists
            result = self.service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range='A1:G1'
            ).execute()
            
            if not result.get('values', []):
                headers = [
                    'Timestamp',
                    'Invoice/Bill Date', 
                    'Invoice/Bill Number',
                    'Amount',
                    'Vendor/Company Name',
                    'Drive File URL',
                    'File Type'
                ]
                body = {'values': [headers]}
                
                result = self.service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range='A1:G1',
                    valueInputOption='RAW',
                    body=body
                ).execute()
                
                print("Headers setup complete")
            else:
                print("Headers already setup")
            return True
            
        except HttpError as error:
            print(f"Error setting up headers: {error}")
            return False