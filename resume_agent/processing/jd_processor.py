import os
import json
from openai import OpenAI
from typing import Dict, List, Any

class JDProcessor:    
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
            
        if not api_key:
            raise ValueError(f"API Key for {self.provider} is missing. Please set it in the sidebar.")

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
    def process(self, jd_text: str) -> Dict[str, Any]:
        prompt = f"""
        Analyze the following Job Description (JD) and extract structured data for a resume screening system.
        
        JD Text:
        {jd_text}
        
        Tasks:
        1. Extract and categorize skills into these specific groups:
           - "core": Main programming languages and frameworks (e.g., Python, React, Java).
           - "security": Auth, OAuth, JWT, penetration testing, security standards.
           - "database": SQL, NoSQL, Redis, migration tools.
           - "devops": Docker, Kubernetes, CI/CD, AWS/Azure, Terraform.
           - "architecture": Microservices, Event-driven, Distributed systems, System Design.
           - "good_to_have": Bonus skills mentioned as "plus" or "preferred".
           
        2. Extract required Years of Experience as a range (min, max). If not specified, estimate based on role level (Junior=0-2, Mid=3-5, Senior=5+).
        
        3. Summarize the role in 2 sentences.
        
        Return ONLY valid JSON in this format:
        {{
            "role_summary": "...",
            "skills": {{
                "core": ["..."],
                "security": ["..."],
                "database": ["..."],
                "devops": ["..."],
                "architecture": ["..."],
                "good_to_have": ["..."]
            }},
            "experience_range": {{
                "min": 2,
                "max": 5
            }}
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise HR Data Extractor. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            print(f"Error processing JD: {e}")
            return {"required_skills": [], "role_summary": "Error parsing JD."}
