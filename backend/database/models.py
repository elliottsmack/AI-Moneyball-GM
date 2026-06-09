from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .db import Base


class Player(Base):
    __tablename__ = "players"

    player_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    age = Column(Integer, nullable=False)
    team = Column(String, nullable=False, index=True)
    position = Column(String, nullable=False, index=True)
    salary = Column(Float, nullable=False)
    war = Column(Float, nullable=False)
    ops = Column(Float, nullable=False)
    obp = Column(Float, nullable=False)
    slg = Column(Float, nullable=False)
    hr = Column(Integer, nullable=False)
    rbi = Column(Integer, nullable=False)
    stolen_bases = Column(Integer, nullable=False)
    mlb_id = Column(Integer, nullable=True)
    data_source = Column(String, nullable=True, default="mock")
    season = Column(Integer, nullable=True)
    games_played = Column(Integer, nullable=True)
    batting_avg = Column(Float, nullable=True)
    last_synced = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Player(name={self.name}, team={self.team}, war={self.war})>"
