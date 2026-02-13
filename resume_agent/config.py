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
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower() # 'openai' or 'groq'

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if LLM_PROVIDER == "groq":
    if not GROQ_API_KEY:
        print("WARNING: GROQ_API_KEY is not set.")
    LLM_API_KEY = GROQ_API_KEY
    LLM_BASE_URL = "https://api.groq.com/openai/v1"
    LLM_MODEL = "llama-3.3-70b-versatile" # Updated model ID
else:
    if not OPENAI_API_KEY:
        print("WARNING: OPENAI_API_KEY is not set.")
    LLM_API_KEY = OPENAI_API_KEY
    LLM_BASE_URL = None # Default OpenAI URL
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
