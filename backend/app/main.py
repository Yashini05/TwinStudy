from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .config import settings
from .db import Base, engine, get_db
from . import models
from .routers import api
from .routers import career
from .routers import resume_intelligence

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Academic Digital Twin API", version="1.0.0")
allowed_origins = list(dict.fromkeys([settings.frontend_origin, *(
    origin.strip() for origin in settings.frontend_origins.split(",") if origin.strip()
)]))
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(api.router, prefix="/api")
app.include_router(career.router, prefix="/api")
app.include_router(resume_intelligence.router, prefix="/api")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
if FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="frontend-assets")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/{path:path}", include_in_schema=False)
def frontend(path: str):
    if not FRONTEND_DIST.is_dir():
        raise HTTPException(status_code=404, detail="Frontend build not found")
    requested = (FRONTEND_DIST / path).resolve()
    if requested.is_file() and FRONTEND_DIST in requested.parents:
        return FileResponse(requested)
    return FileResponse(FRONTEND_DIST / "index.html")
