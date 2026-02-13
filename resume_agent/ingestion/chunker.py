import re
from typing import List, Dict

class ResumeChunker:
    SECTION_HEADERS = [
        "SKILLS", "EXPERIENCE", "WORK EXPERIENCE", "PROJECTS", "EDUCATION", 
        "CERTIFICATIONS", "LANGUAGES", "SUMMARY", "OBJECTIVE", "PUBLICATIONS"
    ]
    
    @staticmethod
    def chunk(text: str) -> List[str]:
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        chunks = []
        current_chunk = []
        lines = text.split('\n')
        
        header_indices = []
        for i, line in enumerate(lines):
            clean_line = line.strip().upper()
            clean_line_no_punct = re.sub(r'[:\-]', '', clean_line).strip()
            
            if clean_line_no_punct in ResumeChunker.SECTION_HEADERS:
                header_indices.append(i)
        
        if not header_indices:
            return [p.strip() for p in text.split('\n\n') if p.strip()]
        
        for i in range(len(header_indices)):
            start = header_indices[i]
            end = header_indices[i+1] if i + 1 < len(header_indices) else len(lines)
            
            section_content = "\n".join(lines[start:end]).strip()
            if section_content:
                chunks.append(section_content)
                
            if i == 0 and start > 0:
                 intro_content = "\n".join(lines[0:start]).strip()
                 if intro_content:
                     chunks.insert(0, intro_content)
                     
        return chunks

    @staticmethod
    def semantic_chunking_fallback(text: str, max_chunk_size: int = 500) -> List[str]:
        return [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
