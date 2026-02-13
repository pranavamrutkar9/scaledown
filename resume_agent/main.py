from ingestion.pdf_parser import PDFParser
from ingestion.chunker import ResumeChunker
from processing.jd_processor import JDProcessor
from retrieval.engine import ResumeRetriever
from compression.compressor import ContextCompressor
from evaluation.matcher import SkillMatcher, CandidateExplainer
import time

class ResumeScreeningAgent:
    def __init__(self):
        self.chunker = ResumeChunker()
        self.jd_processor = JDProcessor()
        self.retriever = ResumeRetriever()
        self.compressor = ContextCompressor()
        self.matcher = SkillMatcher(self.retriever)
        self.explainer = CandidateExplainer()
        
    def run(self, pdf_file, jd_text: str):
        """
        Runs the full screening pipeline.
        
        Args:
            pdf_file: File-like object or path.
            jd_text: Job Description text.
            
        Returns:
            Dictionary containing all analysis results.
        """
        results = {}
        
        # 1. Ingestion
        print("Ingesting PDF...")
        resume_text = PDFParser.extract_text(pdf_file)
        if not resume_text:
            return {"error": "Failed to extract text from PDF."}
            
        resume_chunks = self.chunker.chunk(resume_text)
        results["chunks"] = resume_chunks
        
        # 2. Extract Skills (Categorized)
        print("Processing JD...")
        jd_data = self.jd_processor.process(jd_text)
        required_skills = [] # Flatten for retrieving? Matcher uses full dict now.
        # But retrieval engine still needs a list of strings?
        # Let's flatten skills for retrieval context
        for cat, skills in jd_data.get("skills", {}).items():
            required_skills.extend(skills)
            
        role_summary = jd_data["role_summary"]
        
        # 3. ScaleDown Retrieval
        print("Indexing and Retrieving...")
        self.retriever.index_resume(resume_chunks)
        top_chunks = self.retriever.retrieve(role_summary + " " + " ".join(required_skills), top_k=5)
        
        # 4. Compression (Optional)
        print("Compressing Context...")
        context_text = "\n".join(chunk for chunk in top_chunks)
        if self.compressor:
            compressed_context = self.compressor.compress(context_text, role_summary)
        else:
            compressed_context = context_text[:3000] # Fallback truncation
            
        results["relevant_chunks"] = top_chunks
        results["compressed_context"] = compressed_context

        # 5. Deterministic Matching (Weighted)
        print("Matching Skills...")
        match_data = self.matcher.match(jd_data, resume_text)
        results["match_data"] = match_data
        results["jd_data"] = jd_data
        
        # 6. Final Explanation
        print("Generating Explanation...")
        evaluation = self.explainer.explain(role_summary, jd_data, match_data, compressed_context)
        results["evaluation"] = evaluation
        
        return results
