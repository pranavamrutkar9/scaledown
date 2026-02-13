import pdfplumber
from typing import Optional, Union
from io import BytesIO

class PDFParser:
    @staticmethod
    def extract_text(file_source: Union[str, BytesIO]) -> str:
        text = ""
        try:
            with pdfplumber.open(file_source) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return ""
            
        return text.strip()
