import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agent import analyze_job_fit
from resume_parser import parse_resume
from schemas import JobFitRequest, JobFitResponse

app = FastAPI()

origins = [origin.strip() for origin in os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "AI Job Fit Analyzer backend running"}


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        text = parse_resume(file.filename, file_bytes)

        if not text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from this resume.",
            )

        return {
            "filename": file.filename,
            "resume_text": text,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/analyze", response_model=JobFitResponse)
async def analyze(request: JobFitRequest):
    result = await analyze_job_fit(request.resume_text, request.job_description)
    return JobFitResponse(**result)
