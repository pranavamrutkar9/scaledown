# 📄 Resume Screening Agent

A production-ready **AI Hiring Assistant** that automates technical candidate screening with **90% cost reduction** using Groq (Llama-3) and deterministic scoring.

![Streamlit UI](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Fastest_Inference-orange?style=for-the-badge)

---

## 🚀 Key Features

- **Weighted Scoring Engine**: Calculates score based on weighted categories.
- **Zero Hallucinations**: Uses a **deterministic matching algorithm** for scoring, not LLM vibes.
- **Cost-Free Intelligence**: Powered by **Groq API (Llama-3 70B)** for lightning-fast, free inference.
- **Semantic Search**: Uses `SentenceTransformers` + `FAISS` to find relevant experience even if keywords don't match exactly.
- **Implied Skill Verification**: An LLM agent "reads between the lines" to verify if a candidate has implied skills (e.g., "Built API" -> "REST").
- **Strict Penalties**: Applies logical penalties for "Red Flags" like missing security skills or insufficient experience.

---

## 🛠️ Architecture

The system follows a **Retrieval-Augmented Generation (RAG)** pipeline optimized for recruiting:

1.  **Ingestion**: Extracts text from PDF resumes.
2.  **JD Analysis**: Llama-3 extracts structured skills and requirements from the Job Description.
3.  **Vector Retrieval**: Semantic search finds the most relevant resume sections for each required skill.
4.  **Scoring**:
    - **Exact Match**: 100% points
    - **Strong Semantic**: 80% points
    - **Moderate Semantic**: 50% points
    - **Implied (Verified)**: 40% points
5.  **Explanation**: Llama-3 generates a human-readable summary justifying the score.

---

## 📦 Installation & Usage

**Prerequisites**:
- Python 3.10+
- [Groq API Key](https://console.groq.com/keys) (Free)

### ⚡ One-Click Start (Windows)

Simply run the batch script in the root directory:

```powershell
.\run_app.bat
```

*This automatically manages the virtual environment and dependencies.*

### 🛠️ Manual Installation

```bash
# 1. Create venv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install deps
pip install -r resume_agent/requirements.txt

# 3. Run App
streamlit run resume_agent/app.py
```

---

## ⚙️ Configuration

The app is pre-configured to use **Groq**.

1.  Launch the app.
2.  Paste your **Groq API Key** in the sidebar.
3.  The key is automatically saved to a local `.env` file for future runs.

---

## 📂 Project Structure

```plaintext
scaledown/
├── resume_agent/
│   ├── ingestion/          # PDF Parsing & Chunking
│   ├── processing/         # JD Extraction (LLM)
│   ├── retrieval/          # Semantic Search Engine
│   ├── evaluation/         # Scoring logic & Matcher
│   ├── app.py              # Streamlit UI
│   ├── main.py             # Orchestration Logic
│   └── config.py           # Settings
├── run_app.bat             # Launcher Script
└── README.md               # Documentation
```

## 📄 License

MIT License.
