# Study Squad

FastAPI + Gemini AI backend and static frontend.

## Railway Variables
Set these in Railway (never put the secret key in index.html):
- `GEMINI_API_KEY` — Gemini API key
- `SECRET_KEY` — long random string
- `DATABASE_URL` — optional; defaults to local SQLite

## Local
`python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`

The frontend automatically uses the current website origin, so users do not need to enter an API URL after deployment.

## AI task flow
1. User gives a goal in the AI Task Planner.
2. Gemini creates concrete tasks.
3. User uploads a photo as proof for a task.
4. Gemini vision checks the image against the task.
5. Only an `approved` result marks the task completed.
