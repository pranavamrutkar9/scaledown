# 📄 Resume Screening Agent: Technical Documentation

## 1. Project Overview

This **Resume Screening Agent** is a production-ready system designed to automate the initial screening of technical candidates. It leverages a hybrid approach combining **Statistical NLP (ScaleDown/SentenceTransformers)** for semantic search and retrieval, and **Large Language Models (Llama-3-70b via Groq)** for high-level reasoning and decision-making.

The core philosophy is **"Deterministic Scoring, AI Reasoning"**. We do not let the LLM hallucinate a score. Instead, we calculate a score based on verifiable data points (keyword matches, years of experience, critical penalties) and use the LLM only to explain *why* that score was given.

### key Differentiators
- **Zero Cost Inference**: Uses Groq's free tier (Llama-3).
- **Explainable AI**: Scores are mathematically derived, not Hallucinated.
- **Privacy First**: Resumes are processed locally or in memory; only anonymized snippets are sent to LLM if needed.
- **Optimized for Tokens**: Uses context compression and efficient chunking to minimize LLM context window usage.

---

## 2. System Architecture

The system follows a **RAG (Retrieval-Augmented Generation)** pipeline optimized for recruiting.

### 2.1. Ingestion Layer (`ingestion/`)
- **PDF Parsing**: Uses `pdfplumber` for high-fidelity text extraction.
- **Intelligent Chunking**: Instead of arbitrary character counts, we split resumes by logical sections:
  - *Experience*
  - *Skills*
  - *Projects*
  - *Education*
  
### 2.2. Job Description Processing (`processing/`)
- An LLM (Llama-3) analyzes the raw Job Description (JD) to extract structured data:
  - **Categorized Skills**: `Core`, `Security`, `Database`, `DevOps`, `Architecture`, `Good-to-Have`.
  - **Role Summary**: A 2-sentence breakdown of the core responsibility.
  - **Experience Requirements**: Minimum and maximum years required.

### 2.3. Retrieval Engine (`retrieval/`)
- **Embeddings**: We use `all-MiniLM-L6-v2` (via `SentenceTransformers`) to create vector embeddings of resume chunks.
- **Indexing**: `FAISS` (Facebook AI Similarity Search) creates an in-memory index for sub-millisecond retrieval.
- **Querying**: When checking for a specific skill (e.g., "Kubernetes"), we query the vector index to find the most relevant section of the resume, even if the exact keyword isn't present (Semantic Matching).

---

## 3. Scoring Methodology

The heart of the system is the **Weighted Scoring Engine** (`evaluation/matcher.py`).

### 3.1. Weights Configuration
Different skills have different impacts on the final score:

| Category | Weight | Reason |
| :--- | :--- | :--- |
| **Core Skills** | **50%** | The fundamental languages/frameworks needed for the job. |
| **Security** | **15%** | Critical for modern production apps. |
| **Database** | **15%** | Backend efficiency and data modeling. |
| **DevOps** | **10%** | Deployment and CI/CD awareness. |
| **Good-to-Have** | **10%** | Bonus skills that differentiate candidates. |
| **Architecture** | **0%** | Handled purely via *penalties* (see below). |

### 3.2. Matching Tiers
For every required skill, we determine a "Match Level":

1.  **Exact Match (1.0)**: The keyword exists verbatim in the resume.
2.  **Strong Semantic Match (0.8)**: High vector similarity (>0.80) (e.g., "Postgres" vs "PostgreSQL").
3.  **Moderate Semantic Match (0.5)**: Moderate similarity (>0.65) (e.g., "React" vs "Frontend Development").
4.  **Implied Match (0.4)**: The skill is not explicitly stated but verified by LLM to be implied by other experience (e.g., "Built REST API" implies "HTTP").

### 3.3. Penalty System
We apply strict penalties for critical gaps, modeling "Red Flags":

- **Security Gap (-7%)**: If critical security skills (OAuth, JWT, OWASP) are missing.
- **Architecture Gap (-5%)**: If a senior role is missing System Design patterns.
- **Experience Gap (-20%)**: If the candidate has significantly fewer years of experience than required.
- **Overqualified (-5%)**: If candidate is far too senior (potential flight risk), a small penalty is applied.

---

## 4. Technology Stack

- **Language**: Python 3.10+
- **Frontend**: Streamlit (Custom CSS for "Premium" feel)
- **LLM Provider**: Groq (Llama-3-70b-Versatile)
- **Vector DB**: FAISS (CPU version)
- **Embeddings**: HuggingFace (`sentence-transformers`)
- **PDF Engine**: `pdfplumber`

---

## 5. Installation & Usage

### Prerequisites
- Python installed.
- A free API Key from [Groq Console](https://console.groq.com).

### Quick Start
1.  Clone the repository.
2.  Run the setup script:
    ```powershell
    .\run_app.bat
    ```
3.  The UI will open in your browser.
4.  Enter your Groq API Key in the sidebar.
5.  Upload a PDF Resume and paste a Job Description.

---

## 6. Directory Structure

```plaintext
resume_agent/
├── app.py                 # Streamlit UI Entry point
├── config.py              # Configuration & Environment Variables
├── main.py                # Main orchestration class
├── requirements.txt       # Python dependencies
├── ingestion/             # PDF Parsing & Chunking modules
├── processing/            # JD Analysis modules
├── retrieval/             # Vector search engine
├── evaluation/            # Scoring logic & Matcher
└── compression/           # Context window optimization
```

---

## 7. Future Roadmap

- [ ] **Batch Processing**: Upload zip files of resumes for bulk ranking.
- [ ] **Email Integration**: Auto-draft rejection or interview emails.
- [ ] **Custom Models**: Fine-tune a small BERT model for classification.
