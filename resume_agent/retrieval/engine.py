import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Dict

class ResumeRetriever:
    """Handles semantic indexing and retrieval of resume chunks."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []
        
    def index_resume(self, chunks: List[str]):
        """
        Embeds and indexes resume chunks.
        
        Args:
            chunks: List of text chunks from the resume.
        """
        self.chunks = chunks
        if not chunks:
            return
            
        self.chunk_embeddings = self.model.encode(chunks)
        
        # FAISS Index
        d = self.chunk_embeddings.shape[1]
        self.index = faiss.IndexFlatL2(d)
        self.index.add(np.array(self.chunk_embeddings, dtype=np.float32))
        
    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """
        Retrieves top_k most relevant chunks for the query.
        
        Args:
            query: The search query (Role Summary + Skills).
            top_k: Number of chunks to return.
            
        Returns:
            List of relevant text chunks.
        """
        if not self.index or not self.chunks:
            return []
            
        query_vector = self.model.encode([query])
        k = min(top_k, len(self.chunks))
        
        distances, indices = self.index.search(np.array(query_vector, dtype=np.float32), k)
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.chunks):
                results.append(self.chunks[idx])
                
        return results

    def check_similarity(self, term: str, text_chunks: List[str], threshold: float = 0.75) -> bool:
        """
        Checks if a term is semantically similar to any part of the text chunks.
        Uses cached embeddings if available, otherwise encodes.
        """
        if not self.index:
            return False
            
        term_emb = self.model.encode([term])[0]
        
        # Use cached embeddings if text_chunks matches self.chunks
        # This is a heuristic match, assuming we mostly check against the full resume we indexed.
        if hasattr(self, 'chunk_embeddings') and len(text_chunks) == len(self.chunks) and text_chunks == self.chunks:
            chunk_embs = self.chunk_embeddings
        else:
            chunk_embs = self.model.encode(text_chunks)
        
        from sklearn.metrics.pairwise import cosine_similarity
        if len(chunk_embs) == 0:
            return False
            
        sims = cosine_similarity([term_emb], chunk_embs)
        return np.max(sims) > threshold
