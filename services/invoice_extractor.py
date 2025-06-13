"""
Data extraction service for invoice processing
"""
import io
import base64
from typing import Dict, List
from pdf2image import convert_from_bytes
from PIL import Image
from groq import Groq
import json
from config import GROQ_API_KEY, POPPLER_PATH

# Optional PDF processing
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("PyPDF2 not available. PDF text extraction disabled.")

client = Groq(api_key=GROQ_API_KEY)

class LLMService:
    """Service for interacting with LLM for text extraction. Uses LLm because it is best for scanned images"""
    
    @staticmethod
    def extract_text_from_image(images) -> str:
        try:
            if not isinstance(images, list):
                images = [images]
                
            img_str_arr = []
            for img in images:
                buffered = io.BytesIO()
                img.convert('RGB').save(buffered, format="PNG")
                img_str_arr.append(base64.b64encode(buffered.getvalue()).decode('utf-8'))
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": '''
                            Extract all text from this invoice image in a structured way. Include invoice number, date, vendor name, and total amount if available.
                            Return only valid JSON in this format:
                            {
                            "vendor_name": "...",
                            "invoice_date": "...",
                            "total_amount": "...",
                            "invoice_number": "..."
                            }
                            If any field is not found, use "N/A" as the value.
                            '''
                        }
                    ]
                }
            ]
            
            for img_str in img_str_arr:
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{img_str}"}
                })
            
            response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=messages,
                response_format={"type": "json_object"}
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error extracting text with LLM: {e}")
            return ""

class ExtractionService:
    
    def extract_invoice_data(self, file_data: bytes, filename: str, mime_type: str) -> Dict:
        print(f"Extracting data from {filename} ({mime_type})")
        
        # Initialize with default values
        extracted_data = {
            'invoice_date': 'N/A',
            'vendor_name': 'N/A', 
            'invoice_number': 'N/A',
            'total_amount': 'N/A'
        }
        
        # Extract text based on file type
        text_content = self._extract_text(file_data, mime_type)
        if text_content:
            extracted_data = self._parse_text_content(text_content)
        print(extracted_data)
        return extracted_data
    
    def _extract_text(self, file_data: bytes, mime_type: str) -> str:
        text_content = ""
        
        if mime_type == 'application/pdf':
            images = self._convert_pdf_to_images(file_data)
            if images:
                llm_service = LLMService()
                for img in images:
                    extracted_text = llm_service.extract_text_from_image([img])
                    if extracted_text:
                        text_content += extracted_text + "\n\n"
                            
        elif mime_type.startswith('image/'):
            try:
                image = Image.open(io.BytesIO(file_data))
                llm_service = LLMService()
                text_content = llm_service.extract_text_from_image(image)
            except Exception as e:
                print(f"Error processing image: {e}")
                
        elif mime_type == 'message/rfc822':
            try:
                from email import policy
                from email.parser import BytesParser
                
                # Parse the email
                msg = BytesParser(policy=policy.default).parsebytes(file_data)
                
                # Extract text from email body
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get('Content-Disposition'))
                        
                        # Skip attachments
                        if 'attachment' in content_disposition:
                            continue
                            
                        # Get text/plain or text/html content
                        if content_type == 'text/plain' or content_type == 'text/html':
                            try:
                                payload = part.get_payload(decode=True)
                                if payload:
                                    text_content += payload.decode('utf-8', errors='replace') + "\n\n"
                            except Exception as e:
                                print(f"Error decoding email part: {e}")
                else:
                    # Simple email without multipart
                    try:
                        payload = msg.get_payload(decode=True)
                        if payload:
                            text_content = payload.decode('utf-8', errors='replace')
                    except Exception as e:
                        print(f"Error decoding email: {e}")
                        
                # If no content was extracted, try to get the raw payload
                if not text_content.strip():
                    try:
                        text_content = msg.as_string()
                    except Exception as e:
                        print(f"Error getting raw email content: {e}")
                        
            except Exception as e:
                print(f"Error processing .eml file: {e}")
                # Fallback to basic text extraction
                text_content = file_data.decode('utf-8', errors='ignore')
        
        return text_content.strip()
        
    def _convert_pdf_to_images(self, pdf_data: bytes) -> List[Image.Image]:
        try:
            images = convert_from_bytes(pdf_data, poppler_path=POPPLER_PATH)
            return images
        except Exception as e:
            print(f"Error converting PDF to images: {e}")
            return []
    
    def _extract_pdf_text(self, file_data: bytes) -> str:
        if not PDF_AVAILABLE:
            return ""
            
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_data))
            text_content = ""
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:  # Only add non-empty text
                    text_content += text + "\n"
            return text_content.strip()
        except Exception as e:
            print(f"PDF text extraction failed: {e}")
            return ""
    
    def _parse_text_content(self, text: str) -> Dict:
        try:
            return json.loads(text)
        except Exception as e:
            print(f"Error parsing text content: {e}")
            return {}