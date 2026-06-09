"""
AI Moneyball GM — FastAPI Backend
Phase 2: Live MLB API integration via MLB Stats API + FanGraphs.
Production: serves built React frontend from frontend/dist/
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import inspect, text

from .database.db import engine, SessionLocal
from .database.models import Base
from .services.data_import import DataImportService
from .routers import players, teams, health
from .routers import sync as sync_router

logger = logging.getLogger(__name__)

DIST_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")


def run_migrations():
    """Add any new columns to existing tables without destroying data."""
    inspector = inspect(engine)
    if "players" not in inspector.get_table_names():
        return

    existing_cols = {col["name"] for col in inspector.get_columns("players")}
    new_cols = {
        "mlb_id": "INTEGER",
        "data_source": "VARCHAR",
        "season": "INTEGER",
        "games_played": "INTEGER",
        "batting_avg": "FLOAT",
        "last_synced": "DATETIME",
    }

    with engine.connect() as conn:
        added = []
        for col, col_type in new_cols.items():
            if col not in existing_cols:
                conn.execute(text(f"ALTER TABLE players ADD COLUMN {col} {col_type}"))
                added.append(col)
        if added:
            conn.commit()
            logger.info(f"[migration] Added columns: {added}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    Base.metadata.create_all(bind=engine)

    app.state.is_syncing = False
    app.state.last_sync_result = None
    app.state.last_sync_time = None

    db = SessionLocal()
    try:
        from .database.models import Player as _Player
        from sqlalchemy import or_ as _or
        live_count = db.query(_Player).filter(_Player.data_source == "live").count()
        if live_count > 0:
            logger.info(f"[startup] {live_count} live players already in DB — skipping mock seed")
        else:
            svc = DataImportService(db)
            result = svc.import_mock_data()
            logger.info(
                f"[startup] DB seeded — created={result['created']} skipped={result['skipped']}"
            )
    finally:
        db.close()

    yield


app = FastAPI(
    title="AI Moneyball GM API",
    description="Baseball analytics engine — Phase 2: live MLB Stats API + FanGraphs.",
    version="2.0.0",
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
app.include_router(sync_router.router, prefix="/api")


if os.path.isdir(DIST_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST_DIR, "assets")), name="assets")
    for svg in ["favicon.svg", "icons.svg"]:
        svg_path = os.path.join(DIST_DIR, svg)
        if os.path.exists(svg_path):
            @app.get(f"/{svg}", include_in_schema=False)
            def _serve_svg(p=svg_path):
                return FileResponse(p)

    @app.get("/", include_in_schema=False)
    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str = ""):
        index = os.path.join(DIST_DIR, "index.html")
        if os.path.exists(index):
            return FileResponse(index)
        return {"error": "Frontend not built"}
else:
    @app.get("/")
    def root():
        return {"app": "AI Moneyball GM", "version": "2.0.0", "docs": "/docs"}
