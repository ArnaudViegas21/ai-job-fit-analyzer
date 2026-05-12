import json
import os
import re
from typing import Any, Dict, List

import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama3.2")

REQUIRED_RESPONSE_FIELDS = [
    "match_score",
    "strengths",
    "matched_skills",
    "missing_skills",
    "improvements",
    "resume_suggestions",
    "experience_alignment",
    "concerns",
    "recommended_action",
    "recommendation",
    "final_recommendation",
    "tailored_message",
]


def _ensure_list(value: Any) -> List[str]:
    """Normalize model output into a clean list of strings."""
    if value is None:
        return []

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, str):
        if not value.strip():
            return []
        return [value.strip()]

    return [str(value).strip()]


def _safe_int(value: Any, default: int = 0) -> int:
    """Convert match score to a safe 0-100 integer."""
    try:
        score = int(float(value))
        return max(0, min(score, 100))
    except (TypeError, ValueError):
        return default


def _normalize_string(value: Any) -> str:
    return str(value or "").strip()


def _extract_json(text: str) -> Dict[str, Any]:
    """
    Extract JSON from an LLM response.
    Works even if the model accidentally wraps JSON in extra text.
    """
    if not text:
        return {}

    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {}

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}


def _normalize_recommended_action(value: Any) -> str:
    action = str(value or "Maybe").strip().title()

    if action not in {"Apply", "Maybe", "Skip"}:
        return "Maybe"

    return action


def _normalize_response(parsed: Dict[str, Any]) -> Dict[str, Any]:
    response = {
        "match_score": _safe_int(parsed.get("match_score", 0)),
        "strengths": _ensure_list(parsed.get("strengths")),
        "matched_skills": _ensure_list(parsed.get("matched_skills")),
        "missing_skills": _ensure_list(parsed.get("missing_skills")),
        "improvements": _ensure_list(parsed.get("improvements")),
        "resume_suggestions": _ensure_list(parsed.get("resume_suggestions")),
        "experience_alignment": _normalize_string(parsed.get("experience_alignment")),
        "concerns": _ensure_list(parsed.get("concerns")),
        "recommended_action": _normalize_recommended_action(parsed.get("recommended_action")),
        "recommendation": _normalize_string(parsed.get("recommendation")),
        "final_recommendation": _normalize_string(parsed.get("final_recommendation")),
        "tailored_message": _normalize_string(parsed.get("tailored_message")),
    }

    if not response["strengths"] and response["matched_skills"]:
        response["strengths"] = [
            f"Relevant experience or skill match: {skill}"
            for skill in response["matched_skills"][:5]
        ]

    if not response["improvements"] and response["missing_skills"]:
        response["improvements"] = [
            f"Add or strengthen resume evidence for: {skill}"
            for skill in response["missing_skills"][:5]
        ]

    if not response["resume_suggestions"] and response["improvements"]:
        response["resume_suggestions"] = response["improvements"]

    if not response["recommendation"]:
        if response["recommended_action"] == "Apply":
            response["recommendation"] = (
                "This role appears to be a strong fit. Apply and tailor the resume "
                "to highlight the strongest matching skills."
            )
        elif response["recommended_action"] == "Maybe":
            response["recommendation"] = (
                "This role has some alignment, but the resume should be improved "
                "before applying."
            )
        else:
            response["recommendation"] = (
                "This role does not appear to be a strong fit based on the current resume."
            )

    if not response["final_recommendation"]:
        response["final_recommendation"] = response["recommendation"]

    for field in REQUIRED_RESPONSE_FIELDS:
        if field not in response:
            response[field] = [] if field.endswith("s") else ""

    return response


async def analyze_job_fit(resume_text: str, job_description: str) -> dict:
    prompt = f"""
You are an AI job application analyst.

Analyze the candidate's resume against the job description.

Return ONLY valid JSON with this exact structure:

{{
  "match_score": 0,
  "strengths": [],
  "matched_skills": [],
  "missing_skills": [],
  "improvements": [],
  "resume_suggestions": [],
  "experience_alignment": "",
  "concerns": [],
  "recommended_action": "Apply",
  "recommendation": "",
  "final_recommendation": "",
  "tailored_message": ""
}}

Field rules:
- match_score must be an integer from 0 to 100.
- strengths must be a list of the candidate's strongest relevant advantages.
- matched_skills must be a list of exact or closely related skills found in both the resume and job description.
- missing_skills must be a list of important job requirements not clearly shown in the resume.
- improvements must be a list of specific ways to improve the resume for this role.
- resume_suggestions must be a list of resume bullet or content suggestions.
- experience_alignment must briefly explain how well the candidate's background fits the role.
- concerns must be a list of honest concerns or gaps.
- recommended_action must be exactly one of: Apply, Maybe, Skip.
- recommendation must be a short practical recommendation.
- final_recommendation must be a recruiter/job-seeker friendly final summary.
- tailored_message must be a short outreach message the candidate could send to a recruiter.

Scoring guidance:
- 85-100: Strong fit. Most requirements are clearly demonstrated.
- 70-84: Good fit. Several strong matches with some gaps.
- 50-69: Partial fit. Some relevant experience, but important gaps.
- 25-49: Weak fit. Limited alignment.
- 0-24: Poor fit. Resume does not match the role well.

Important rules:
- Be honest and specific.
- Do not invent experience.
- Do not assume skills unless clearly supported by the resume.
- Base your answer only on the resume and job description.
- Return JSON only.
- Do not use markdown.
- Do not include explanations outside the JSON.

Resume:
{resume_text}

Job Description:
{job_description}
"""

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {"temperature": 0.2},
                },
            )

        response.raise_for_status()
        data = response.json()
        content = data.get("response", "{}")
        parsed = _extract_json(content)
        return _normalize_response(parsed)

    except httpx.ConnectError:
        return {
            "match_score": 0,
            "strengths": [],
            "matched_skills": [],
            "missing_skills": [],
            "improvements": [
                "Start Ollama locally before running the analysis."
            ],
            "resume_suggestions": [],
            "experience_alignment": "Could not connect to the local Ollama server.",
            "concerns": [
                "Ollama is not running on http://localhost:11434."
            ],
            "recommended_action": "Maybe",
            "recommendation": "Start Ollama and try again.",
            "final_recommendation": "The analysis could not run because the local AI model is unavailable.",
            "tailored_message": "",
        }

    except Exception as error:
        return {
            "match_score": 0,
            "strengths": [],
            "matched_skills": [],
            "missing_skills": [],
            "improvements": [],
            "resume_suggestions": [],
            "experience_alignment": "The local model could not complete the analysis.",
            "concerns": [str(error)],
            "recommended_action": "Maybe",
            "recommendation": "Try again after checking the backend and Ollama logs.",
            "final_recommendation": "The analysis failed due to a backend or model response issue.",
            "tailored_message": "",
        }