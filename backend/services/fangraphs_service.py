"""
Stats Enrichment Service
------------------------
Fetches WAR (bWAR) from Baseball Reference via pybaseball,
and salary data from the FanGraphs public API.
No authentication required.
"""
import logging
import unicodedata
from datetime import date
from typing import Optional

logger = logging.getLogger(__name__)

MLB_MINIMUM_SALARY = 740000

BREF_TEAM_TO_STD: dict[str, str] = {
    "KCR": "KC",
    "SDP": "SD",
    "SFG": "SF",
    "TBR": "TB",
    "WSN": "WSH",
    "CHW": "CWS",
    "CHC": "CHC",
    "LAA": "LAA",
    "LAD": "LAD",
    "NYM": "NYM",
    "NYY": "NYY",
    "PHI": "PHI",
}


def normalize_name(name: str) -> str:
    """Normalize player name for fuzzy matching (remove accents, lowercase)."""
    nfkd = unicodedata.normalize("NFKD", str(name))
    ascii_name = "".join(c for c in nfkd if not unicodedata.combining(c))
    return ascii_name.lower().strip()


def _safe_float(v, default: float = 0.0) -> float:
    try:
        return float(v) if v is not None else default
    except (ValueError, TypeError):
        return default


class FanGraphsService:
    """
    Fetches bWAR from Baseball Reference (via pybaseball) and
    salary data from the FanGraphs public API.
    """

    def __init__(self, season: Optional[int] = None):
        self.season = season or date.today().year

    def fetch_war_and_salary(self) -> dict:
        """
        Returns two dicts:
          war_by_mlb_id: { mlb_id_int -> float }       — primary matching
          war_by_name:   { normalized_name -> float }   — fallback matching
          salary_by_name: { normalized_name -> float }  — from FanGraphs
        """
        war_by_id, war_by_name = self._fetch_bwar()
        salary_by_name = self._fetch_fg_salary()

        return {
            "war_by_mlb_id": war_by_id,
            "war_by_name": war_by_name,
            "salary_by_name": salary_by_name,
        }

    def _fetch_bwar(self) -> tuple[dict[int, float], dict[str, float]]:
        """
        Fetch Baseball Reference bWAR for hitters using pybaseball.
        Returns (war_by_mlb_id, war_by_normalized_name).
        """
        import warnings
        warnings.filterwarnings("ignore")

        by_id: dict[int, float] = {}
        by_name: dict[str, float] = {}

        try:
            from pybaseball import bwar_bat
            df_all = bwar_bat(return_all=True)
            df = df_all[df_all["year_ID"] == self.season].copy()

            if df.empty and self.season == date.today().year:
                prev = self.season - 1
                logger.info(f"bWAR: no data for {self.season}, trying {prev}")
                df = df_all[df_all["year_ID"] == prev].copy()

            logger.info(f"bWAR: {len(df)} hitter rows for season {df['year_ID'].iloc[0] if not df.empty else '?'}")

            # Aggregate by player (handle multiple stints with same team via sum)
            # Group by mlb_ID first for most accurate matching
            agg = df.groupby("mlb_ID", as_index=False).agg(
                name_common=("name_common", "first"),
                WAR=("WAR", "sum"),
            )

            for _, row in agg.iterrows():
                war = _safe_float(row.get("WAR"))
                name = str(row.get("name_common", ""))
                mlb_id_raw = row.get("mlb_ID")

                if not name:
                    continue

                key = normalize_name(name)
                by_name[key] = war

                if mlb_id_raw is not None:
                    try:
                        mlb_id = int(float(mlb_id_raw))
                        if mlb_id > 0:
                            by_id[mlb_id] = war
                    except (ValueError, TypeError):
                        pass

            logger.info(f"bWAR: {len(by_id)} by mlb_id, {len(by_name)} by name")
        except Exception as e:
            logger.warning(f"bWAR fetch failed: {e}")

        return by_id, by_name

    def _fetch_fg_salary(self) -> dict[str, float]:
        """
        Fetch salary data from FanGraphs public API (type=0 standard view).
        Returns { normalized_name -> salary_float }.
        """
        import httpx

        salary_map: dict[str, float] = {}
        try:
            headers = {
                "User-Agent": "AI-Moneyball-GM/2.0 analytics",
                "Referer": "https://www.fangraphs.com/leaders/major-league",
                "Accept": "application/json",
            }
            params = {
                "age": 0,
                "pos": "all",
                "stats": "bat",
                "lg": "all",
                "qual": 1,
                "season": self.season,
                "season1": self.season,
                "pageitems": 500,
                "pagenum": 1,
                "ind": 0,
                "rost": 0,
                "players": 0,
                "type": 0,
                "postseason": "false",
            }
            with httpx.Client(timeout=httpx.Timeout(30.0)) as client:
                resp = client.get(
                    "https://www.fangraphs.com/api/leaders/major-league/data",
                    params=params,
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()

            rows = data.get("data", [])
            for row in rows:
                if not isinstance(row, dict):
                    continue
                name = row.get("PlayerName") or row.get("PlayerNameRoute") or ""
                raw_sal = row.get("Salary") or row.get("salary")
                if not name or raw_sal is None:
                    continue
                try:
                    sal = float(str(raw_sal).replace(",", "").replace("$", ""))
                    if sal > 0:
                        salary_map[normalize_name(name)] = sal
                except (ValueError, TypeError):
                    continue

            logger.info(f"FanGraphs salary: {len(salary_map)} entries for {self.season}")
        except Exception as e:
            logger.warning(f"FanGraphs salary fetch failed: {e}")

        return salary_map


KNOWN_SALARIES_2025: dict[str, float] = {
    "shohei ohtani": 46000000,
    "aaron judge": 40000000,
    "mike trout": 37116666,
    "trea turner": 35714285,
    "fernando tatis jr.": 34800000,
    "francisco lindor": 34100000,
    "corey seager": 32500000,
    "rafael devers": 31250000,
    "mookie betts": 30000000,
    "marcus semien": 29000000,
    "freddie freeman": 27000000,
    "bryce harper": 27538462,
    "paul goldschmidt": 26000000,
    "yordan alvarez": 26000000,
    "masataka yoshida": 26000000,
    "nolan arenado": 35000000,
    "j.t. realmuto": 23000000,
    "austin riley": 22000000,
    "matt olson": 21000000,
    "xander bogaerts": 20000000,
    "pete alonso": 20000000,
    "ronald acuna jr.": 17000000,
    "kyle tucker": 13000000,
    "jose ramirez": 14000000,
    "vladimir guerrero jr.": 14000000,
    "salvador perez": 13000000,
    "max muncy": 13500000,
    "bryan reynolds": 13500000,
    "luis robert jr.": 12500000,
    "ha-seong kim": 7000000,
    "anthony santander": 7000000,
    "jake cronenworth": 6750000,
    "jazz chisholm jr.": 6200000,
    "jeff mcneil": 8750000,
    "nathaniel lowe": 5250000,
    "cedric mullins": 5100000,
    "daulton varsho": 4000000,
    "julio rodriguez": 4000000,
    "wander franco": 2000000,
    "jonah heim": 2600000,
    "bobby witt jr.": 9090909,
    "gunnar henderson": 720000,
    "adley rutschman": 728000,
    "elly de la cruz": 720000,
    "corbin carroll": 730000,
    "spencer steer": 720000,
    "josh jung": 720000,
    "cj abrams": 720000,
    "jackson holliday": 720000,
}


def estimate_salary(name: str, age: int, war: float) -> float:
    """
    Estimate salary when no market data is available.
    Pre-arb (<3 yrs service, ~age<=25): MLB minimum.
    Arb years: scale with WAR. Veteran: market rate.
    """
    key = normalize_name(name)
    if key in KNOWN_SALARIES_2025:
        return KNOWN_SALARIES_2025[key]
    if age <= 25:
        return MLB_MINIMUM_SALARY
    if age <= 27:
        return max(MLB_MINIMUM_SALARY, round(war * 900_000))
    base = max(2_000_000, round(war * 1_600_000))
    return min(base, 25_000_000)
