"""
AI Moneyball GM — FastAPI Backend
Production: serves built React frontend from frontend/dist/
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database.db import engine, SessionLocal
from .database.models import Base
from .services.data_import import DataImportService
from .routers import players, teams, health

DIST_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        svc = DataImportService(db)
        result = svc.import_mock_data()
        print(f"[startup] DB seeded — created={result['created']} skipped={result['skipped']}")
    finally:
        db.close()
    yield


app = FastAPI(
    title="AI Moneyball GM API",
    description="Baseball analytics engine. Phase 1: data pipeline & player browser.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(players.router, prefix="/api")
app.include_router(teams.router, prefix="/api")


if os.path.isdir(DIST_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST_DIR, "assets")), name="assets")

    @app.get("/", include_in_schema=False)
    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str = ""):
        index = os.path.join(DIST_DIR, "index.html")
        if os.path.exists(index):
            return FileResponse(index)
        return {"error": "Frontend not built. Run: cd frontend && npm run build"}
else:
    @app.get("/")
    def root():
        return {"app": "AI Moneyball GM", "version": "1.0.0", "docs": "/docs"}
