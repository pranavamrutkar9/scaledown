import os
import sys
from dotenv import load_dotenv

load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
scaledown_path = os.path.join(parent_dir, "scaledown")

if scaledown_path not in sys.path:
    sys.path.append(scaledown_path)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if LLM_PROVIDER == "groq":
    if not GROQ_API_KEY:
        print("Waiting for GROQ_API_KEY...")
    LLM_API_KEY = GROQ_API_KEY
    LLM_BASE_URL = "https://api.groq.com/openai/v1"
    LLM_MODEL = "llama-3.3-70b-versatile"
else:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LLM_API_KEY = OPENAI_API_KEY
    LLM_BASE_URL = None
    LLM_MODEL = "gpt-4o"

SCALEDOWN_API_KEY = os.getenv("SCALEDOWN_API_KEY")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
SIMILARITY_THRESHOLD = 0.75

MATCH_THRESHOLD = 75
