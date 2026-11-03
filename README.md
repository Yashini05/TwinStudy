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

## Single-service production deployment

The production frontend is built into `frontend/dist` and served by FastAPI from the same origin. API calls use the relative `/api` path in production, while local development continues to use the separate Vite and FastAPI servers.

Build and start from the repository root on a Linux-based hosting service:

```bash
npm --prefix frontend ci
npm --prefix frontend run build
python -m pip install -r backend/requirements.txt
cd backend
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Configure the service with:

- **Build command:** `npm --prefix frontend ci && npm --prefix frontend run build && python -m pip install -r backend/requirements.txt`
- **Release/migration command:** `cd backend && alembic upgrade head`
- **Start command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health check path:** `/health`

Required production environment variables:

```text
DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:<port>/<database>
SECRET_KEY=<long-random-secret>
ACCESS_TOKEN_EXPIRE_MINUTES=60
FRONTEND_ORIGIN=https://<your-public-domain>
FRONTEND_ORIGINS=https://<your-public-domain>
UPLOAD_DIR=/var/data/uploads
```

### Durable document storage

Resume and uploaded job-description originals use a private storage adapter. Local development uses `UPLOAD_DIR`. Production stores the original bytes in PostgreSQL (`BYTEA`) so the application can run on Render Free without R2, a paid subscription, or a persistent Render disk. The 5 MB per-file limit protects the free database allocation; monitor Neon usage as documents accumulate.

The following optional variables support an existing private R2 bucket, but they are not required for deployment and should remain unset when using Neon-backed storage:

```text
APP_ENV=production
R2_ACCOUNT_ID=<cloudflare-account-id>
R2_ACCESS_KEY_ID=<r2-access-key-id>
R2_SECRET_ACCESS_KEY=<r2-secret-access-key>
R2_BUCKET_NAME=<private-bucket-name>
R2_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
```

With the default production configuration, PostgreSQL records store each document's private key, storage backend, and original bytes. Downloads and deletion require authentication and the owning student. Upload metadata and bytes commit atomically, and deleting the database row removes the stored bytes. `UPLOAD_DIR` remains available for local development and is ignored by Git. Database-backed storage is simple and genuinely free, but consumes Neon database storage and is not appropriate for unlimited large-file hosting.

Do not set `VITE_API_URL` for the single-service build unless it is the public same-origin `/api` path. Never use a localhost URL in the production frontend.

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
