from typing import List, Dict, Any
from retrieval.engine import ResumeRetriever
from processing.jd_processor import JDProcessor
from openai import OpenAI
import os
import json
import re

# Ensure config is loaded
try:
    from resume_agent.config import OPENAI_API_KEY
except ImportError:
    pass

class SkillMatcher:
    def __init__(self, retriever: ResumeRetriever):
        self.retriever = retriever
        
    def match(self, jd_data: Dict[str, Any], resume_text: str) -> Dict[str, Any]:
        """
        Matches skills using weighted categories and deterministic penalties.
        """
        jd_skills = jd_data.get("skills", {})
        exp_range = jd_data.get("experience_range", {})
        
        # 1. Extract Candidate Experience
        candidate_exp = self._extract_experience(resume_text)
        
        # 2. Categorized Scoring
        scores = {}
        details = {}
        
        # Weights
        weights = {
            "core": 0.50,
            "security": 0.15,
            "database": 0.15,
            "devops": 0.10,
            "good_to_have": 0.10,
            "architecture": 0.0 # Handled via penalty
        }
        
        # Filter existing categories to normalize weights
        present_categories = [cat for cat in weights if jd_skills.get(cat)]
        if not present_categories:
            return {"error": "No skills found in JD", "match_score": 0, "matched_skills": [], "missing_skills": []}
            
        total_weight = sum(weights[cat] for cat in present_categories)
        normalized_weights = {cat: weights[cat] / total_weight for cat in present_categories}
        
        # Initial stats collection
        category_stats = {}
        all_missing_for_verification = []
        
        for category in present_categories:
            skills = jd_skills[category]
            if not skills: continue
            
            # Initial deterministic check
            points, matched, missing = self._initial_check(skills, resume_text)
            
            category_stats[category] = {
                "points": points,
                "matched": matched,
                "missing": missing,
                "total_skills": len(skills),
                "weight": normalized_weights[category]
            }
            
            # Architecture skills are NOT guessed/implied per strict rules
            if category != "architecture":
                for m in missing:
                    all_missing_for_verification.append(m)

        # 3. Batch LLM Verification for Implied Skills
        verified_implied = {} # skill_lower -> True
        if all_missing_for_verification:
            # Deduplicate
            unique_missing = list(set(all_missing_for_verification))
            verified_names = self._verify_implied_skills(unique_missing, resume_text)
            for v in verified_names:
                verified_implied[v.lower()] = True
        
        # 4. Final Score Calculation
        weighted_score = 0
        all_matched_final = []
        all_missing_final = []
        
        for category, stats in category_stats.items():
            final_matched = list(stats["matched"])
            final_missing = []
            
            current_points = stats["points"]
            
            for missing_skill in stats["missing"]:
                # If architecture, strict rule applies (no implied points)
                if category == "architecture":
                    final_missing.append(missing_skill)
                    continue
                    
                # Check if verified
                if verified_implied.get(missing_skill.lower()) or self._is_fuzzy_found(missing_skill, verified_implied):
                    current_points += 0.4 # Implied point value
                    final_matched.append(f"{missing_skill} (Implied)")
                else:
                    final_missing.append(missing_skill)
            
            # Calculate category score
            cat_score = (current_points / stats["total_skills"]) * 100
            weighted_score += cat_score * stats["weight"]
            
            details[category] = {"matched": final_matched, "missing": final_missing}
            all_matched_final.extend(final_matched)
            all_missing_final.extend(final_missing)

        # 5. Penalties
        final_score = weighted_score
        penalties = []
        
        # A. Security Penalty
        if "security" in details and details["security"]["missing"]:
             final_score *= 0.93
             penalties.append(f"Missing Critical Security Skills (-7%)")

        # B. Architecture Penalty
        if "architecture" in details and details["architecture"]["missing"]:
            final_score *= 0.95
            penalties.append("Missing Architecture Patterns (-5%)")

        # C. Experience Penalty
        if exp_range and candidate_exp > 0:
            min_exp = float(exp_range.get("min", 0))
            max_exp = float(exp_range.get("max", 100))
            
            if candidate_exp < min_exp:
                final_score *= 0.80
                penalties.append(f"Experience Gap: {candidate_exp}y vs {min_exp}y+ (-20%)")
            elif candidate_exp > max_exp + 3:
                final_score *= 0.95
                penalties.append(f"Overqualified: {candidate_exp}y vs {max_exp}y (-5%)")

        # Determine Confidence
        if final_score >= 85: confidence = "High"
        elif final_score >= 65: confidence = "Medium"
        else: confidence = "Low"

        return {
            "match_score": round(final_score, 1),
            "confidence_level": confidence,
            "matched_skills": all_matched_final,
            "missing_skills": all_missing_final,
            "applied_penalties": penalties,
            "details": details,
            "candidate_experience": candidate_exp
        }

    def _initial_check(self, skills, resume_text):
        matched = []
        missing = []
        points = 0
        resume_lower = resume_text.lower()
        
        for skill in skills:
            s_lower = skill.lower()
            if s_lower in resume_lower:
                points += 1.0
                matched.append(skill)
                continue
                
            # Fuzzy
            if self.retriever.check_similarity(skill, self.retriever.chunks, threshold=0.80):
                 points += 0.8
                 matched.append(f"{skill} (Strong)")
            elif self.retriever.check_similarity(skill, self.retriever.chunks, threshold=0.65):
                 points += 0.5
                 matched.append(f"{skill} (Moderate)")
            else:
                 missing.append(skill)
        return points, matched, missing

    def _verify_implied_skills(self, missing_skills, resume_text):
        if not missing_skills: return []
        try:
            provider = os.getenv("LLM_PROVIDER", "openai").lower()
            if provider == "groq":
                api_key = os.getenv("GROQ_API_KEY")
                base_url = "https://api.groq.com/openai/v1"
                model = "llama-3.3-70b-versatile"
            else:
                api_key = os.getenv("OPENAI_API_KEY")
                base_url = None
                model = "gpt-4o"
            
            if not api_key: return []

            client = OpenAI(api_key=api_key, base_url=base_url)
            truncated = resume_text[:15000]
            
            prompt = f"""
            You are a technical recruiter.
            The system marked these skills as MISSING: {json.dumps(missing_skills)}
            
            Read the resume context:
            {truncated}
            
            Identify which "missing" skills are ACTUALLY present or strictly implied.
            IMPORTANT: Return the exact skill name from the list.
            Return JSON: {{ "present_skills": ["ExactName", ...] }}
            """
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            data = json.loads(response.choices[0].message.content)
            return data.get("present_skills", [])
        except:
            return []

    def _is_fuzzy_found(self, skill, verified_dict):
        s_lower = skill.lower()
        for v_skill in verified_dict:
            if s_lower == v_skill or s_lower in v_skill or v_skill in s_lower:
                return True
        return False

    def _extract_experience(self, text: str) -> float:
        # Regex Heuristic
        try:
            matches = re.findall(r'(\d+)(?:\+)?\s*(?:-|to)?\s*(?:\d+)?\s*years?', text.lower())
            if matches:
                 # Logic for regex is weak, skip to LLM for reliability
                 pass
        except: pass
        
        # LLM Extraction
        try:
            provider = os.getenv("LLM_PROVIDER", "openai").lower()
            if provider == "groq":
                 client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
                 model = "llama-3.3-70b-versatile"
            else:
                 client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                 model = "gpt-4o"
            
            if not client.api_key: return 0.0

            prompt = f"Extract total years of relevant experience from this resume. Return ONLY a number (e.g. 3.5). If not found, return 0.\n\nContext: {text[:5000]}"
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10
            )
            content = resp.choices[0].message.content
            match = re.search(r"[\d\.]+", content)
            return float(match.group()) if match else 0.0
        except:
            return 0.0

class CandidateExplainer:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        if self.provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            base_url = "https://api.groq.com/openai/v1"
            self.model = "llama-3.3-70b-versatile"
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = None
            self.model = "gpt-4o"
        
        if api_key:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = None

    def explain(self, 
                role_summary: str, 
                jd_data: Dict[str, Any], 
                match_data: Dict[str, Any], 
                resume_context: str) -> Dict[str, Any]:
        
        if not self.client: return {"error": "No API Key"}

        # Format skills for prompt
        skills_text = json.dumps(jd_data.get("skills", {}), indent=2)
        
        prompt = f"""
        You are an expert HR Recruiter. Evaluate this candidate based on the detailed scoring analysis.
        
        Role: {role_summary}
        Required Skills Structure:
        {skills_text}
        
        Scoring Data:
        - Match Score: {match_data['match_score']}%
        - Confidence: {match_data.get('confidence_level', 'Medium')}
        - Penalties Applied: {json.dumps(match_data.get('applied_penalties', []))}
        - Matched Skills: {json.dumps(match_data['matched_skills'])}
        - Missing Skills: {json.dumps(match_data['missing_skills'])}
        - Candidate Experience: {match_data.get('candidate_experience', 0)} years
        
        Resume Context (Compressed):
        {resume_context}
        
        Task:
        1. Explain the score. Why did they get {match_data['match_score']}? Mention specific penalties or bonuses.
        2. List key strengths.
        3. List key gaps (especially critical missing skills).
        4. Provide hiring recommendation: "Strong Fit", "Moderate Fit", or "Weak Fit" consistent with the score/confidence.
        
        Constraint: You CANNOT change the score. You must justify the calculated score.
        
        Return JSON:
        {{
            "explanation": ["..."],
            "strengths": ["..."],
            "gaps": ["..."],
            "recommendation": "..."
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": str(e)}
