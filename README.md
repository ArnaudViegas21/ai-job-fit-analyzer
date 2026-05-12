# AI Job Fit Analyzer

AI Job Fit Analyzer is a resume-to-job-description matching tool that uses a local AI model to score fit, identify matched and missing skills, and suggest resume improvements.

## What it does

- Extracts text from uploaded resumes (`PDF`, `DOCX`, `TXT`)
- Compares the resume against a pasted job description
- Uses local Ollama inference to generate:
  - match score
  - strengths
  - matched skills
  - missing skills
  - resume improvement suggestions
  - recruiter-facing tailored message

## Architecture

- `backend/` — FastAPI server
  - resume upload parsing
  - Ollama prompt generation and JSON normalization
  - analysis API
- `frontend/` — Next.js app
  - resume upload UI
  - job description editor
  - results dashboard

## Tech stack

- Python 3.x
- FastAPI
- httpx
- pypdf
- python-docx
- Next.js 16
- React 19
- Tailwind CSS
- Ollama local model inference

## Quick start

### 1. Start the backend

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start the frontend

In a separate terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` in your browser.

## Local AI requirement

This project requires a local Ollama server.

- Default Ollama endpoint: `http://localhost:11434/api/generate`
- Default model: `llama3.2`

If Ollama is not running, the analysis endpoint will return a helpful failure response.

## Configuration

### Backend environment variables

- `OLLAMA_URL` — full Ollama API endpoint (default: `http://localhost:11434/api/generate`)
- `OLLAMA_MODEL_NAME` — Ollama model name (default: `llama3.2`)
- `CORS_ORIGINS` — comma-separated allowed origins for frontend access (default: `http://localhost:3000,http://127.0.0.1:3000`)

### Frontend environment variable

- `NEXT_PUBLIC_API_URL` — backend URL (default: `http://localhost:8000`)

## Testing

Run backend tests with:

```powershell
cd backend
pytest
```

## Notes

- Resume uploads are validated client-side for type and size.
- The backend normalizes model responses into a stable JSON schema.
- The frontend displays analysis results and raw AI output for debugging.

## Future improvements

- add support for more resume formats
- deploy a remote AI backend option
- add GitHub Actions CI for test coverage
- add better UX for analyzer errors and retries
