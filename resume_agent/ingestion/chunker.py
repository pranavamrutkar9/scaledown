import re
from typing import List, Dict

class ResumeChunker:
    """Splits resume text into logical chunks."""
    
    # Common resume section headers
    SECTION_HEADERS = [
        "SKILLS", "EXPERIENCE", "WORK EXPERIENCE", "PROJECTS", "EDUCATION", 
        "CERTIFICATIONS", "LANGUAGES", "SUMMARY", "OBJECTIVE", "PUBLICATIONS"
    ]
    
    @staticmethod
    def chunk(text: str) -> List[str]:
        """
        Splits text into logical chunks based on headers.
        Fallback to paragraph/newline splitting if no headers found.
        """
        # Normalize text: remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Identify headers
        # We look for lines that match the headers (case-insensitive) 
        # distinctively on their own line
        
        chunks = []
        current_chunk = []
        lines = text.split('\n')
        
        # Simple heuristic: if a line is short, uppercase, and in our list, it's a header
        header_indices = []
        for i, line in enumerate(lines):
            clean_line = line.strip().upper()
            # Check for exact match or match with slight noise (e.g. "Skills:")
            clean_line_no_punct = re.sub(r'[:\-]', '', clean_line).strip()
            
            if clean_line_no_punct in ResumeChunker.SECTION_HEADERS:
                header_indices.append(i)
        
        if not header_indices:
            # Fallback: Split by double newlines (paragraphs)
            return [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Slice based on indices
        for i in range(len(header_indices)):
            start = header_indices[i]
            end = header_indices[i+1] if i + 1 < len(header_indices) else len(lines)
            
            # The section content
            section_content = "\n".join(lines[start:end]).strip()
            if section_content:
                chunks.append(section_content)
                
            # If there was text BEFORE the first header (e.g. Name, Contact), capture it
            if i == 0 and start > 0:
                 intro_content = "\n".join(lines[0:start]).strip()
                 if intro_content:
                     chunks.insert(0, intro_content) # Insert at beginning
                     
        return chunks

    @staticmethod
    def semantic_chunking_fallback(text: str, max_chunk_size: int = 500) -> List[str]:
        """Backup chunking if structure is poor."""
        return [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
