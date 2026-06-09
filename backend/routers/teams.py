from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database.db import get_db
from ..services.player_service import PlayerService

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("")
def get_teams(db: Session = Depends(get_db)):
    svc = PlayerService(db)
    teams = svc.get_teams()
    return {"teams": teams}


@router.get("/positions")
def get_positions(db: Session = Depends(get_db)):
    svc = PlayerService(db)
    positions = svc.get_positions()
    return {"positions": positions}
