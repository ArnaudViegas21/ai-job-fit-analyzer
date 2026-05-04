from pydantic import BaseModel
from typing import List


class JobFitRequest(BaseModel):
    resume: str
    job_description: str


class JobFitResponse(BaseModel):
    match_score: int
    matched_skills: List[str]
    missing_skills: List[str]
    experience_alignment: str
    concerns: List[str]
    recommended_action: str
    tailored_message: str