import streamlit as st
import os
import sys

# Ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import ResumeScreeningAgent
import config

# Page Config
st.set_page_config(
    page_title="Resume Screening Agent",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for "Premium" feel
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        height: 50px;
        font-weight: bold;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .skill-tag {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 15px;
        margin: 3px;
        font-size: 0.9em;
    }
    .matched {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .missing {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

st.title("📄 Token-Optimized Resume Screening Agent")
st.markdown("Powered by **ScaleDown** & OpenAI")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    
    # Provider Selection
    provider = st.radio("Select Logic Provider", ["OpenAI", "Groq (Free)"], index=1)
    
    if provider == "Groq (Free)":
        os.environ["LLM_PROVIDER"] = "groq"
        
        # Check session state or env
        default_groq = st.session_state.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
        
        api_key = st.text_input("Groq API Key", type="password", value=default_groq, placeholder="gsk-...")
        
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
            st.session_state["GROQ_API_KEY"] = api_key
            st.success("Groq Key Set!")
            
        st.markdown("[Get Free Groq Key](https://console.groq.com/keys)")
    else:
        os.environ["LLM_PROVIDER"] = "openai"
        
        # Check session state or env
        default_openai = st.session_state.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
        
        api_key = st.text_input("OpenAI API Key", type="password", value=default_openai, placeholder="sk-...")
        
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            st.session_state["OPENAI_API_KEY"] = api_key
            st.success("OpenAI Key Set!")
    
    st.info("Upload a resume and paste the job description to get a detailed analysis.")

    # Re-import config to pick up new env vars if changed
    import importlib
    importlib.reload(config)

# Input Section
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Job Description")
    jd_text = st.text_area("Paste JD here...", height=300, placeholder="Software Engineer role requires Python, AWS...")

with col2:
    st.subheader("2. Upload Resume")
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])

if st.button("Evaluate Candidate", type="primary", use_container_width=True):
    if not jd_text or not uploaded_file:
        st.error("Please provide both a Job Description and a Resume.")
    else:
        # Run Agent
        agent = ResumeScreeningAgent()
        
        with st.spinner("Analyzing Candidate... (Ingesting, Chunking, Retrieving, Matching)"):
            try:
                # Reset file pointer if needed
                uploaded_file.seek(0)
                results = agent.run(uploaded_file, jd_text)
                
                if "error" in results:
                    st.error(results["error"])
                else:
                    st.success("Analysis Complete!")
                    
                    match_data = results["match_data"]
                    evaluation = results["evaluation"]
                    
                    # --- SCORES SECTION ---
                    st.divider()
                    
                    score = match_data["match_score"]
                    confidence = match_data.get("confidence_level", "Medium")
                    
                    # Color code
                    if score >= 85:
                        score_color = "#28a745" # Green
                    elif score >= 65:
                        score_color = "#ffc107" # Orange
                    else:
                        score_color = "#dc3545" # Red
                    
                    col_metrics, col_rec = st.columns(2)
                    
                    with col_metrics:
                         st.markdown(f"""
                        <div class="metric-card" style="color: #000;">
                            <h3>Match Score</h3>
                            <div style="font-size: 3em; font-weight: bold; color: {score_color};">
                                {score}%
                            </div>
                            <div style="color: #666; font-size: 0.9em;">Confidence: {confidence}</div>
                            <progress value="{score}" max="100" style="width: 100%"></progress>
                        </div>
                        """, unsafe_allow_html=True)
                        
                         # Penalties
                         penalties = match_data.get("applied_penalties", [])
                         if penalties:
                            st.warning("⚠️ Applied Adjustments:")
                            for p in penalties:
                                st.write(f"- {p}")

                    with col_rec:
                         rec = evaluation.get("recommendation", "N/A")
                         rec_color = "#28a745" if "Strong" in rec else "#ffc107" if "Moderate" in rec else "#dc3545"
                         st.markdown(f"""
                        <div class="metric-card" style="color: #000;">
                            <h3>Recommendation</h3>
                            <div style="font-size: 2em; font-weight: bold; color: {rec_color}; margin-top: 20px;">
                                {rec}
                            </div>
                            <div style="margin-top: 10px;">
                                {results['jd_data'].get('experience_range', {}).get('min', 0)}+ Years Exp Required
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # --- SKILLS SECTION ---
                    st.divider()
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.subheader("✅ Matched Skills")
                        if match_data["matched_skills"]:
                            for skill in match_data["matched_skills"]:
                                st.markdown(f'<span class="skill-tag matched">{skill}</span>', unsafe_allow_html=True)
                        else:
                            st.write("No matches.")
                            
                    with col_b:
                        st.subheader("❌ Missing Skills")
                        if match_data["missing_skills"]:
                            for skill in match_data["missing_skills"]:
                                st.markdown(f'<span class="skill-tag missing">{skill}</span>', unsafe_allow_html=True)
                        else:
                            st.write("None.")
                    
                    # --- ANALYSIS SECTION ---
                    st.divider()
                    with st.expander("Detailed Analysis", expanded=True):
                        st.markdown("### 📝 Explanation")
                        for point in evaluation.get("explanation", []):
                            st.markdown(f"- {point}")
                            
                        col_str, col_gap = st.columns(2)
                        with col_str:
                            st.markdown("#### 💪 Strengths")
                            for s in evaluation.get("strengths", []):
                                st.markdown(f"- {s}")
                        with col_gap:
                            st.markdown("#### ⚠️ Key Gaps")
                            for g in evaluation.get("gaps", []):
                                st.markdown(f"- {g}")
                                
                    with st.expander("Technical Details (JSON)"):
                         st.json(match_data)
                         
                    with st.expander("Resume Context (Top Chunks)"):
                        st.markdown("### Relevant Resume Chunks (Top 5)")
                        for i, chunk in enumerate(results["relevant_chunks"]):
                            st.text_area(f"Chunk {i+1}", chunk[:500] + "...", height=100)

            except Exception as e:
                st.error(f"An error occurred: {e}")
                import traceback
                st.code(traceback.format_exc())
