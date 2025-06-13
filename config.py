"""
Configuration settings for Gmail automation
"""
import os
from typing import List
from dotenv import load_dotenv
load_dotenv()
# Google API Configuration
SCOPES: List[str] = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/spreadsheets'
]

# File paths
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"

# Google Services IDs (Replace with your actual IDs)
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")
DRIVE_FOLDER_NAME = os.getenv("DRIVE_FOLDER_NAME", "Viable Test Documents")

# Email processing settings
TARGET_SUBJECT = "Viable: Trial Document"
GMAIL_LABEL_NAME = "Processed"

#Groq API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

POPPLER_PATH = r"C:\poppler\Library\bin"
# Supported file types
SUPPORTED_MIME_TYPES = [
    'application/pdf',
    'image/jpeg', 
    'image/png',
    'message/rfc822',  # For .eml files
]

# Automation settings
SCHEDULE_HOURS = 3