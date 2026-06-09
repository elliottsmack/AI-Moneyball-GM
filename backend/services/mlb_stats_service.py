"""
MLB Stats API Service
---------------------
Fetches live player data from statsapi.mlb.com (free, no auth required).
Returns normalized, deduplicated player dicts ready for database import.
"""
import httpx
import logging
from datetime import date
from typing import Optional

logger = logging.getLogger(__name__)

MLB_BASE = "https://statsapi.mlb.com/api/v1"

TEAM_ABBREV: dict[str, str] = {
    "Arizona Diamondbacks": "ARI",
    "Atlanta Braves": "ATL",
    "Baltimore Orioles": "BAL",
    "Boston Red Sox": "BOS",
    "Chicago Cubs": "CHC",
    "Chicago White Sox": "CWS",
    "Cincinnati Reds": "CIN",
    "Cleveland Guardians": "CLE",
    "Colorado Rockies": "COL",
    "Detroit Tigers": "DET",
    "Houston Astros": "HOU",
    "Kansas City Royals": "KC",
    "Los Angeles Angels": "LAA",
    "Los Angeles Dodgers": "LAD",
    "Miami Marlins": "MIA",
    "Milwaukee Brewers": "MIL",
    "Minnesota Twins": "MIN",
    "New York Mets": "NYM",
    "New York Yankees": "NYY",
    "Oakland Athletics": "OAK",
    "Philadelphia Phillies": "PHI",
    "Pittsburgh Pirates": "PIT",
    "San Diego Padres": "SD",
    "San Francisco Giants": "SF",
    "Seattle Mariners": "SEA",
    "St. Louis Cardinals": "STL",
    "Tampa Bay Rays": "TB",
    "Texas Rangers": "TEX",
    "Toronto Blue Jays": "TOR",
    "Washington Nationals": "WSH",
    "Athletics": "OAK",
}


def _abbrev(team_name: str, api_abbrev: str = "") -> str:
    if api_abbrev:
        return api_abbrev
    return TEAM_ABBREV.get(team_name, team_name[:3].upper() if team_name else "UNK")


def _safe_float(v, default: float = 0.0) -> float:
    try:
        return float(v) if v is not None else default
    except (ValueError, TypeError):
        return default


def _safe_int(v, default: int = 0) -> int:
    try:
        return int(v) if v is not None else default
    except (ValueError, TypeError):
        return default


class MLBStatsService:
    """Fetches and deduplicates player stats from the free MLB Stats API."""

    def __init__(self, season: Optional[int] = None):
        self.season = season or date.today().year
        self.timeout = httpx.Timeout(45.0)
        self.headers = {"User-Agent": "AI-Moneyball-GM/2.0 analytics"}

    def fetch_qualified_hitters(self) -> list[dict]:
        """
        Fetch qualified hitters with full hitting stats for the season.
        Returns deduplicated list (one entry per player, multi-team stints merged).
        Falls back to previous season if current season has too few qualifiers.
        """
        players = self._fetch_and_merge(self.season, "qualified")

        if len(players) < 30 and self.season == date.today().year:
            logger.info(f"Only {len(players)} qualified for {self.season}, trying All pool")
            players = self._fetch_and_merge(self.season, "All", min_games=30)

        if len(players) < 30:
            prev = self.season - 1
            logger.info(f"Falling back to {prev} season")
            players = self._fetch_and_merge(prev, "qualified")

        logger.info(f"MLB Stats API: {len(players)} unique hitters for {self.season}")
        return players

    def _fetch_and_merge(self, season: int, player_pool: str, min_games: int = 0) -> list[dict]:
        """Fetch splits and merge multi-team stints per player."""
        splits = self._fetch_raw_splits(season, player_pool)
        if not splits:
            return []

        by_id: dict[int, dict] = {}

        for split in splits:
            try:
                player_node = split.get("player", {})
                team_node = split.get("team", {})
                split_position = split.get("position", {})
                stat = split.get("stat", {})

                name = player_node.get("fullName", "")
                if not name:
                    continue

                mlb_id = player_node.get("id")
                if not mlb_id:
                    continue

                team_name = team_node.get("name", "")
                team_abbrev = _abbrev(team_name, team_node.get("abbreviation", ""))

                # player_node contains full profile when hydrate=person is used
                # (data lives in 'player', not the empty 'person' key)
                position = (
                    split_position.get("abbreviation")
                    or player_node.get("primaryPosition", {}).get("abbreviation")
                    or "DH"
                )

                birth_date = player_node.get("birthDate", "")
                current_age = player_node.get("currentAge")
                if birth_date:
                    try:
                        age = season - int(birth_date[:4])
                    except (ValueError, IndexError):
                        age = int(current_age) if current_age else 28
                elif current_age:
                    # currentAge is as of today; adjust back to the target season year
                    today_year = date.today().year
                    age = max(18, int(current_age) - (today_year - season))
                else:
                    age = 28

                games = _safe_int(stat.get("gamesPlayed"))
                obp = _safe_float(stat.get("obp"))
                slg = _safe_float(stat.get("slg"))
                ops = _safe_float(stat.get("ops")) or round(obp + slg, 3)

                stint: dict = {
                    "mlb_id": mlb_id,
                    "name": name,
                    "age": age,
                    "team": team_abbrev,
                    "position": position,
                    "ops": ops,
                    "obp": obp,
                    "slg": slg,
                    "hr": _safe_int(stat.get("homeRuns")),
                    "rbi": _safe_int(stat.get("rbi")),
                    "stolen_bases": _safe_int(stat.get("stolenBases")),
                    "games_played": games,
                    "batting_avg": _safe_float(stat.get("avg")),
                    "season": season,
                    "_ab": _safe_int(stat.get("atBats")),
                    "_hits": _safe_int(stat.get("hits")),
                    "_pa": _safe_int(stat.get("plateAppearances")) or games,
                }

                if mlb_id not in by_id:
                    by_id[mlb_id] = stint
                else:
                    # Merge multi-team stints — accumulate counting stats,
                    # weight-average rate stats by at-bats
                    existing = by_id[mlb_id]
                    total_ab = existing["_ab"] + stint["_ab"]
                    total_hits = existing["_hits"] + stint["_hits"]
                    total_pa = existing["_pa"] + stint["_pa"]

                    merged = {
                        **existing,
                        "hr": existing["hr"] + stint["hr"],
                        "rbi": existing["rbi"] + stint["rbi"],
                        "stolen_bases": existing["stolen_bases"] + stint["stolen_bases"],
                        "games_played": existing["games_played"] + stint["games_played"],
                        "_ab": total_ab,
                        "_hits": total_hits,
                        "_pa": total_pa,
                    }
                    # Recalculate rate stats from totals
                    if total_ab > 0:
                        merged["batting_avg"] = round(total_hits / total_ab, 3)
                    # Keep OBP/SLG/OPS from the stint with more PA (most representative)
                    if stint["_pa"] > existing["_pa"]:
                        merged["obp"] = stint["obp"]
                        merged["slg"] = stint["slg"]
                        merged["ops"] = stint["ops"]
                        merged["team"] = stint["team"]
                    # Use valid age from whichever stint has a real birth_date
                    if existing["age"] == 28 and stint["age"] != 28:
                        merged["age"] = stint["age"]
                    elif existing["age"] != 28:
                        merged["age"] = existing["age"]

                    by_id[mlb_id] = merged

            except Exception as e:
                logger.debug(f"Error parsing split: {e}")
                continue

        players = [
            {k: v for k, v in p.items() if not k.startswith("_")}
            for p in by_id.values()
            if not min_games or p.get("games_played", 0) >= min_games
        ]

        return players

    def _fetch_raw_splits(self, season: int, player_pool: str) -> list[dict]:
        url = (
            f"{MLB_BASE}/stats"
            f"?stats=season"
            f"&group=hitting"
            f"&playerPool={player_pool}"
            f"&season={season}"
            f"&sportId=1"
            f"&limit=500"
            f"&hydrate=person"
        )
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url, headers=self.headers)
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            logger.error(f"MLB Stats API request failed: {e}")
            return []

        splits = []
        for stat_group in data.get("stats", []):
            splits.extend(stat_group.get("splits", []))
        return splits
