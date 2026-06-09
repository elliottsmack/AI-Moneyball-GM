from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from ..database.db import get_db
from ..services.player_service import PlayerService, compute_value_score

router = APIRouter(prefix="/players", tags=["players"])


class PlayerResponse(BaseModel):
    player_id: int
    name: str
    age: int
    team: str
    position: str
    salary: float
    war: float
    ops: float
    obp: float
    slg: float
    hr: int
    rbi: int
    stolen_bases: int

    class Config:
        from_attributes = True


class PlayerWithScore(PlayerResponse):
    value_score: float


@router.get("", response_model=list[PlayerResponse])
def get_players(
    search: Optional[str] = Query(None, description="Search by player name"),
    position: Optional[str] = Query(None, description="Filter by position"),
    team: Optional[str] = Query(None, description="Filter by team"),
    sort_by: str = Query("war", description="Sort field: war, salary, ops, age, hr, rbi"),
    sort_dir: str = Query("desc", description="Sort direction: asc or desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    svc = PlayerService(db)
    return svc.get_all(search=search, position=position, team=team,
                       sort_by=sort_by, sort_dir=sort_dir, skip=skip, limit=limit)


@router.get("/undervalued", response_model=list[PlayerWithScore])
def get_undervalued(
    top_n: int = Query(20, ge=1, le=50, description="Number of top undervalued players"),
    db: Session = Depends(get_db),
):
    svc = PlayerService(db)
    results = svc.get_undervalued(top_n=top_n)
    output = []
    for item in results:
        p = item["player"]
        output.append(PlayerWithScore(
            player_id=p.player_id,
            name=p.name,
            age=p.age,
            team=p.team,
            position=p.position,
            salary=p.salary,
            war=p.war,
            ops=p.ops,
            obp=p.obp,
            slg=p.slg,
            hr=p.hr,
            rbi=p.rbi,
            stolen_bases=p.stolen_bases,
            value_score=item["value_score"],
        ))
    return output


@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: int, db: Session = Depends(get_db)):
    svc = PlayerService(db)
    player = svc.get_by_id(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player
