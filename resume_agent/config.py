import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add ScaleDown to system path
# Assuming scaledown is in the parent directory of resume_agent
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
scaledown_path = os.path.join(parent_dir, "scaledown")

if scaledown_path not in sys.path:
    sys.path.append(scaledown_path)

# LLM Configuration
# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()

# API Keys
# OPENAI_API_KEY is no longer used by default
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if LLM_PROVIDER == "groq":
    # Default to Groq
    if not GROQ_API_KEY:
        print("Waiting for GROQ_API_KEY...")
    LLM_API_KEY = GROQ_API_KEY
    LLM_BASE_URL = "https://api.groq.com/openai/v1"
    LLM_MODEL = "llama-3.3-70b-versatile"
else:
    # Fallback support if manually set env var
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LLM_API_KEY = OPENAI_API_KEY
    LLM_BASE_URL = None
    LLM_MODEL = "gpt-4o"

# ScaleDown Settings
SCALEDOWN_API_KEY = os.getenv("SCALEDOWN_API_KEY") # Optional if using API
EMBEDDING_MODEL = "all-MiniLM-L6-v2" # Fast, efficient model for text

# Processing Settings
CHUNK_SIZE = 500  # Characters (approx 100-150 tokens)
CHUNK_OVERLAP = 50
SIMILARITY_THRESHOLD = 0.75

# Evaluation
MATCH_THRESHOLD = 75 # Percentage
