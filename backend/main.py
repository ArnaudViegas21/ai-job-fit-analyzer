from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas import JobFitRequest, JobFitResponse
from agent import analyze_job_fit

app = FastAPI(title="AI Job Fit Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "Backend is running"}


@app.post("/analyze", response_model=JobFitResponse)
def analyze(request: JobFitRequest):
    result = analyze_job_fit(
        resume=request.resume,
        job_description=request.job_description
    )
    return result