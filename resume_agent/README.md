# Resume Screening Agent

A minimal, production-ready Resume Screening Agent powered by **ScaleDown**, **OpenAI**, and **Streamlit**.

## Features

- **PDF Resume Ingestion**: Automatically extracts and chunks text.
- **JD Processing**: Extracts required skills and role summary using LLM.
- **Semantic Retrieval**: Uses `ScaleDown` (actually FAISS + SentenceTransformers) to find relevant resume sections.
- **Deterministic Skill Matching**: Hybrid Exact + Fuzzy (Semantic) matching.
- **Context Compression**: Reduces token usage using `ScaleDown` compressor.
- **LLM Explanation**: Provides detailed strengths, gaps, and hiring recommendations.

## Prerequisites

- Python 3.10+
- OpenAI API Key
- ScaleDown Repository (cloned as a sibling or inside)

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   - Create a `.env` file in `resume_agent/` or export them:
     ```
     OPENAI_API_KEY=sk-...
     SCALEDOWN_API_KEY=sk-... (Optional)
     ```

## Usage

Run the Streamlit app:

```bash
cd resume_agent
streamlit run app.py
```

## Structure

- `app.py`: UI entry point.
- `main.py`: Core logic orchestrator.
- `ingestion/`: Parsing and chunking.
- `processing/`: JD extraction.
- `retrieval/`: Semantic search engine.
- `evaluation/`: Matching and explanation logic.
