from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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


@app.get("/health")
def health():
    return {"status": "ok"}
