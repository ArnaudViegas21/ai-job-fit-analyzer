import json
import requests


def analyze_job_fit(resume: str, job_description: str) -> dict:
    prompt = f"""
You are an AI job application analyst.

Analyze the candidate's resume against the job description.

Return ONLY valid JSON with this exact structure:

{{
  "match_score": 0,
  "matched_skills": [],
  "missing_skills": [],
  "experience_alignment": "",
  "concerns": [],
  "recommended_action": "Apply",
  "tailored_message": ""
}}

Rules:
- match_score must be an integer from 0 to 100.
- matched_skills must be a list of strings.
- missing_skills must be a list of strings.
- concerns must be a list of strings.
- recommended_action must be one of: Apply, Maybe, Skip.
- Be honest and specific.
- Do not invent experience.
- Base your answer only on the resume and job description.
- Return JSON only. Do not use markdown.

Resume:
{resume}

Job Description:
{job_description}
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.2
                }
            },
            timeout=180
        )

        response.raise_for_status()

        data = response.json()
        content = data.get("response", "{}")

        parsed = json.loads(content)

        return {
            "match_score": int(parsed.get("match_score", 0)),
            "matched_skills": parsed.get("matched_skills", []),
            "missing_skills": parsed.get("missing_skills", []),
            "experience_alignment": parsed.get("experience_alignment", ""),
            "concerns": parsed.get("concerns", []),
            "recommended_action": parsed.get("recommended_action", "Maybe"),
            "tailored_message": parsed.get("tailored_message", "")
        }

    except Exception as error:
        return {
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "experience_alignment": "The local Ollama model could not complete the analysis.",
            "concerns": [str(error)],
            "recommended_action": "Maybe",
            "tailored_message": ""
        }