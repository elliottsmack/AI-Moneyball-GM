"""
AI Moneyball GM — FastAPI Backend
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database.db import engine, SessionLocal
from .database.models import Base
from .services.data_import import DataImportService
from .routers import players, teams, health


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

app.include_router(health.router)
app.include_router(players.router)
app.include_router(teams.router)


@app.get("/")
def root():
    return {"app": "AI Moneyball GM", "version": "1.0.0", "docs": "/docs"}
