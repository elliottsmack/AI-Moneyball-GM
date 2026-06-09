"""
Player Service
--------------
Business logic layer for player operations.

The value_score calculation currently uses WAR/salary.
Phase 3 upgrade: Replace compute_value_score with an ML model prediction.
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..database.models import Player


def compute_value_score(war: float, salary: float) -> float:
    """
    Calculate a player's value score.

    Current: Simple WAR-per-dollar metric (WAR / salary_in_millions).
    Phase 3 upgrade: Replace this function with an ML model that incorporates
    advanced metrics, park factors, age curves, and contract length.
    """
    if salary <= 0:
        return 0.0
    salary_millions = salary / 1_000_000
    return round(war / salary_millions, 4)


class PlayerService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        search: Optional[str] = None,
        position: Optional[str] = None,
        team: Optional[str] = None,
        sort_by: str = "war",
        sort_dir: str = "desc",
        skip: int = 0,
        limit: int = 100,
    ) -> list[Player]:
        query = self.db.query(Player)

        if search:
            query = query.filter(Player.name.ilike(f"%{search}%"))
        if position:
            query = query.filter(Player.position == position)
        if team:
            query = query.filter(Player.team == team)

        sort_col_map = {
            "war": Player.war,
            "salary": Player.salary,
            "ops": Player.ops,
            "age": Player.age,
            "hr": Player.hr,
            "rbi": Player.rbi,
            "name": Player.name,
        }
        sort_col = sort_col_map.get(sort_by, Player.war)
        if sort_dir == "asc":
            query = query.order_by(sort_col.asc())
        else:
            query = query.order_by(sort_col.desc())

        return query.offset(skip).limit(limit).all()

    def get_by_id(self, player_id: int) -> Optional[Player]:
        return self.db.query(Player).filter(Player.player_id == player_id).first()

    def get_undervalued(self, top_n: int = 20) -> list[dict]:
        """
        Return top N undervalued players ranked by value_score.
        Phase 3: Replace compute_value_score with ML model.
        """
        players = self.db.query(Player).all()
        scored = []
        for p in players:
            score = compute_value_score(p.war, p.salary)
            scored.append({"player": p, "value_score": score})

        scored.sort(key=lambda x: x["value_score"], reverse=True)
        return scored[:top_n]

    def get_teams(self) -> list[str]:
        rows = self.db.query(Player.team).distinct().order_by(Player.team).all()
        return [r[0] for r in rows]

    def get_positions(self) -> list[str]:
        rows = self.db.query(Player.position).distinct().order_by(Player.position).all()
        return [r[0] for r in rows]

    def get_stats_summary(self) -> dict:
        players = self.db.query(Player).all()
        if not players:
            return {"total": 0, "avg_salary": 0, "avg_war": 0, "avg_ops": 0}
        total = len(players)
        avg_salary = sum(p.salary for p in players) / total
        avg_war = sum(p.war for p in players) / total
        avg_ops = sum(p.ops for p in players) / total
        return {
            "total": total,
            "avg_salary": round(avg_salary, 2),
            "avg_war": round(avg_war, 2),
            "avg_ops": round(avg_ops, 4),
        }
