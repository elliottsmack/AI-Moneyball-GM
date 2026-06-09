"""
Sync Router
-----------
Endpoints for triggering and checking the status of live MLB data syncs.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, BackgroundTasks, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database.db import get_db
from ..database.models import Player
from ..services.data_import import DataImportService

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("")
def trigger_sync(
    request: Request,
    background_tasks: BackgroundTasks,
    season: int = None,
    db: Session = Depends(get_db),
):
    """
    Trigger a live data sync from MLB Stats API + FanGraphs.
    Runs synchronously and returns the result when complete.
    """
    state = request.app.state
    if getattr(state, "is_syncing", False):
        return {"status": "already_running", "message": "A sync is already in progress"}

    state.is_syncing = True
    try:
        svc = DataImportService(db)
        result = svc.import_live_data(season=season)
        state.last_sync_result = result
        state.last_sync_time = datetime.now(timezone.utc).isoformat()
        return {"status": "complete", **result}
    except Exception as e:
        error_result = {"error": str(e), "source": "failed"}
        state.last_sync_result = error_result
        return {"status": "error", "message": str(e)}
    finally:
        state.is_syncing = False


@router.get("/status")
def sync_status(request: Request, db: Session = Depends(get_db)):
    """
    Return current data state: source (live/mock), player counts,
    season, last sync time.
    """
    state = request.app.state

    total = db.query(func.count(Player.player_id)).scalar() or 0
    from sqlalchemy import or_
    live_count = db.query(func.count(Player.player_id)).filter(Player.data_source == "live").scalar() or 0
    mock_count = (
        db.query(func.count(Player.player_id))
        .filter(or_(Player.data_source == "mock", Player.data_source.is_(None)))
        .scalar() or 0
    )

    latest_sync = (
        db.query(func.max(Player.last_synced))
        .filter(Player.data_source == "live")
        .scalar()
    )
    season_row = (
        db.query(Player.season)
        .filter(Player.data_source == "live", Player.season.isnot(None))
        .first()
    )
    season = season_row[0] if season_row else None

    data_source = "live" if live_count > 0 else "mock"

    return {
        "data_source": data_source,
        "season": season,
        "player_count": total,
        "live_count": live_count,
        "mock_count": mock_count,
        "last_synced": latest_sync.isoformat() if latest_sync else getattr(state, "last_sync_time", None),
        "is_syncing": getattr(state, "is_syncing", False),
        "last_sync_result": getattr(state, "last_sync_result", None),
    }
