from pydantic import BaseModel, Field
from typing import List


class JobFitRequest(BaseModel):
    resume_text: str = Field(..., alias="resume_text")
    job_description: str = Field(..., alias="job_description")

    class Config:
        allow_population_by_field_name = True


class JobFitResponse(BaseModel):
    match_score: int
    strengths: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    improvements: List[str]
    resume_suggestions: List[str]
    experience_alignment: str
    concerns: List[str]
    recommended_action: str
    recommendation: str
    final_recommendation: str
    tailored_message: str