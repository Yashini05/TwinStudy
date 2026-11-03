# TwinStudy

TwinStudy is a full-stack student intelligence platform with an Academic Digital Twin, Career Digital Twin, and deterministic Resume & Job Description Intelligence module. It stores student-owned academic and career evidence, calculates explainable indicators, and provides actionable learning and career preparation guidance.

## Features

- JWT authentication with student-level data isolation.
- Academic Digital Twin for subjects, assessments, attendance, study activity, predictions, risks, recommendations, history, and read-only what-if simulation.
- Career Digital Twin for profiles, skills, projects, experience, certifications, readiness analysis, skill gaps, roadmap tasks, and snapshots.
- Resume and Job Intelligence for PDF/DOCX upload, reviewable extraction, saved job descriptions, Career Twin alignment scoring, evidence-aware gaps, project relevance, comparison history, and preparation tasks.
- Deterministic and explainable baselines when no external AI provider is configured. Alignment scores are not hiring probabilities.

## Architecture

- `backend/`: FastAPI application, SQLAlchemy models, Pydantic schemas, JWT security, analytics engines, Alembic migrations, and tests.
- `frontend/`: React, TypeScript, Vite, Axios, Recharts, and Lucide UI.
- `backend/app/models.py`: academic, career, resume, job, comparison, and roadmap persistence models.
- `backend/app/routers/`: authenticated API surfaces under `/api`, `/api/career`, and `/api/intelligence`.
- `backend/alembic/versions/`: reproducible database migrations.
- Local development uses SQLite; PostgreSQL is supported through `DATABASE_URL`.

## Technologies

Python, FastAPI, SQLAlchemy, Alembic, Pydantic, SQLite/PostgreSQL, JWT, scikit-learn, pypdf, python-docx, React, TypeScript, Vite, Axios, Recharts, Lucide, Vitest.

## Run locally

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

The default local database is SQLite. Set `DATABASE_URL` in `.env` to a PostgreSQL URL for deployment and replace `SECRET_KEY` with a long random value. Never commit `.env`, credentials, uploaded resumes, or local database files.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL` in `frontend/.env` when the API is not at the default URL. API documentation is available at `http://localhost:8000/docs`.

## Verification

```powershell
cd backend
python -m pytest tests -q
alembic check

cd ..\frontend
npm test -- --run
npm run build
```

The backend tests cover authentication, protected routes, academic isolation, Career Twin CRUD/readiness, Resume/Job matching, validation, persistence, and student isolation.

## Core workflow

Register, complete the profile, add subjects, academic records, attendance, and study activities. The dashboard calculates the academic digital twin from those records. The Career Twin stores career evidence separately. Resume & Jobs accepts PDF/DOCX resumes and saved job descriptions, then produces deterministic, explainable alignment scores from the existing Career Twin; extracted resume content requires confirmation and original files are preserved. Predictions use a transparent heuristic until enough historical records exist for a scikit-learn model. What-if simulations never write to academic records.
