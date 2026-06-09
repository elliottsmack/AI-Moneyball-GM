"""
Data Import Service
-------------------
Responsible for populating the database with player data.

Currently uses mock data. Designed so future MLB API integrations
(e.g., MLB Stats API, Baseball Reference, FanGraphs) can replace
the mock data source by implementing the same interface.
"""
import pandas as pd
from sqlalchemy.orm import Session
from ..database.models import Player


MOCK_PLAYERS = [
    {"name": "Aaron Judge", "age": 32, "team": "NYY", "position": "RF", "salary": 40000000, "war": 9.3, "ops": 1.049, "obp": 0.406, "slg": 0.643, "hr": 62, "rbi": 131, "stolen_bases": 16},
    {"name": "Mookie Betts", "age": 31, "team": "LAD", "position": "RF", "salary": 30000000, "war": 8.2, "ops": 0.891, "obp": 0.369, "slg": 0.522, "hr": 39, "rbi": 107, "stolen_bases": 14},
    {"name": "Freddie Freeman", "age": 34, "team": "LAD", "position": "1B", "salary": 27000000, "war": 5.9, "ops": 0.952, "obp": 0.407, "slg": 0.545, "hr": 29, "rbi": 102, "stolen_bases": 5},
    {"name": "Paul Goldschmidt", "age": 36, "team": "STL", "position": "1B", "salary": 26000000, "war": 3.5, "ops": 0.823, "obp": 0.358, "slg": 0.465, "hr": 22, "rbi": 89, "stolen_bases": 3},
    {"name": "Francisco Lindor", "age": 30, "team": "NYM", "position": "SS", "salary": 34100000, "war": 6.7, "ops": 0.858, "obp": 0.348, "slg": 0.510, "hr": 26, "rbi": 98, "stolen_bases": 22},
    {"name": "Trea Turner", "age": 31, "team": "PHI", "position": "SS", "salary": 35714285, "war": 5.2, "ops": 0.831, "obp": 0.341, "slg": 0.490, "hr": 26, "rbi": 76, "stolen_bases": 30},
    {"name": "Nolan Arenado", "age": 33, "team": "STL", "position": "3B", "salary": 35000000, "war": 4.8, "ops": 0.831, "obp": 0.358, "slg": 0.473, "hr": 26, "rbi": 93, "stolen_bases": 2},
    {"name": "Jose Ramirez", "age": 31, "team": "CLE", "position": "3B", "salary": 14000000, "war": 6.2, "ops": 0.855, "obp": 0.366, "slg": 0.489, "hr": 29, "rbi": 126, "stolen_bases": 20},
    {"name": "Yordan Alvarez", "age": 26, "team": "HOU", "position": "DH", "salary": 26000000, "war": 5.4, "ops": 0.990, "obp": 0.406, "slg": 0.584, "hr": 37, "rbi": 97, "stolen_bases": 1},
    {"name": "Vladimir Guerrero Jr.", "age": 25, "team": "TOR", "position": "1B", "salary": 14000000, "war": 5.1, "ops": 0.895, "obp": 0.391, "slg": 0.504, "hr": 26, "rbi": 102, "stolen_bases": 2},
    {"name": "Julio Rodriguez", "age": 23, "team": "SEA", "position": "CF", "salary": 4000000, "war": 5.3, "ops": 0.840, "obp": 0.338, "slg": 0.502, "hr": 32, "rbi": 75, "stolen_bases": 37},
    {"name": "Bobby Witt Jr.", "age": 23, "team": "KC", "position": "SS", "salary": 9090909, "war": 6.1, "ops": 0.861, "obp": 0.326, "slg": 0.535, "hr": 30, "rbi": 97, "stolen_bases": 49},
    {"name": "Corey Seager", "age": 30, "team": "TEX", "position": "SS", "salary": 32500000, "war": 4.5, "ops": 0.861, "obp": 0.368, "slg": 0.493, "hr": 33, "rbi": 96, "stolen_bases": 2},
    {"name": "Marcus Semien", "age": 33, "team": "TEX", "position": "2B", "salary": 29000000, "war": 4.2, "ops": 0.789, "obp": 0.329, "slg": 0.460, "hr": 26, "rbi": 89, "stolen_bases": 15},
    {"name": "Jeff McNeil", "age": 31, "team": "NYM", "position": "2B", "salary": 8750000, "war": 3.8, "ops": 0.773, "obp": 0.382, "slg": 0.391, "hr": 9, "rbi": 62, "stolen_bases": 3},
    {"name": "Gunnar Henderson", "age": 22, "team": "BAL", "position": "SS", "salary": 720000, "war": 6.8, "ops": 0.898, "obp": 0.357, "slg": 0.541, "hr": 28, "rbi": 82, "stolen_bases": 9},
    {"name": "Adley Rutschman", "age": 26, "team": "BAL", "position": "C", "salary": 728000, "war": 5.8, "ops": 0.849, "obp": 0.378, "slg": 0.471, "hr": 20, "rbi": 80, "stolen_bases": 4},
    {"name": "Salvador Perez", "age": 33, "team": "KC", "position": "C", "salary": 13000000, "war": 2.1, "ops": 0.763, "obp": 0.294, "slg": 0.469, "hr": 23, "rbi": 76, "stolen_bases": 0},
    {"name": "J.T. Realmuto", "age": 33, "team": "PHI", "position": "C", "salary": 23000000, "war": 3.9, "ops": 0.798, "obp": 0.340, "slg": 0.458, "hr": 22, "rbi": 84, "stolen_bases": 16},
    {"name": "Bryce Harper", "age": 31, "team": "PHI", "position": "1B", "salary": 27538462, "war": 4.7, "ops": 0.918, "obp": 0.394, "slg": 0.524, "hr": 21, "rbi": 72, "stolen_bases": 10},
    {"name": "Mike Trout", "age": 32, "team": "LAA", "position": "CF", "salary": 37116666, "war": 1.2, "ops": 0.796, "obp": 0.373, "slg": 0.423, "hr": 10, "rbi": 27, "stolen_bases": 0},
    {"name": "Shohei Ohtani", "age": 29, "team": "LAD", "position": "DH", "salary": 46000000, "war": 9.1, "ops": 1.066, "obp": 0.412, "slg": 0.654, "hr": 44, "rbi": 95, "stolen_bases": 20},
    {"name": "Ronald Acuna Jr.", "age": 26, "team": "ATL", "position": "RF", "salary": 17000000, "war": 4.5, "ops": 0.854, "obp": 0.374, "slg": 0.480, "hr": 15, "rbi": 50, "stolen_bases": 73},
    {"name": "Austin Riley", "age": 27, "team": "ATL", "position": "3B", "salary": 22000000, "war": 3.8, "ops": 0.863, "obp": 0.351, "slg": 0.512, "hr": 37, "rbi": 97, "stolen_bases": 2},
    {"name": "Matt Olson", "age": 30, "team": "ATL", "position": "1B", "salary": 21000000, "war": 4.4, "ops": 0.879, "obp": 0.371, "slg": 0.508, "hr": 54, "rbi": 139, "stolen_bases": 3},
    {"name": "Luis Robert Jr.", "age": 26, "team": "CWS", "position": "CF", "salary": 12500000, "war": 2.2, "ops": 0.779, "obp": 0.316, "slg": 0.463, "hr": 38, "rbi": 80, "stolen_bases": 20},
    {"name": "Elly De La Cruz", "age": 21, "team": "CIN", "position": "SS", "salary": 720000, "war": 4.2, "ops": 0.802, "obp": 0.338, "slg": 0.464, "hr": 23, "rbi": 87, "stolen_bases": 67},
    {"name": "Corbin Carroll", "age": 23, "team": "ARI", "position": "CF", "salary": 730000, "war": 1.8, "ops": 0.692, "obp": 0.307, "slg": 0.385, "hr": 11, "rbi": 51, "stolen_bases": 23},
    {"name": "Pete Alonso", "age": 29, "team": "NYM", "position": "1B", "salary": 20000000, "war": 3.0, "ops": 0.834, "obp": 0.341, "slg": 0.493, "hr": 46, "rbi": 118, "stolen_bases": 1},
    {"name": "Kyle Tucker", "age": 27, "team": "HOU", "position": "RF", "salary": 13000000, "war": 5.2, "ops": 0.877, "obp": 0.381, "slg": 0.496, "hr": 29, "rbi": 89, "stolen_bases": 20},
    {"name": "Nathaniel Lowe", "age": 28, "team": "TEX", "position": "1B", "salary": 5250000, "war": 3.1, "ops": 0.799, "obp": 0.366, "slg": 0.433, "hr": 17, "rbi": 76, "stolen_bases": 5},
    {"name": "Jazz Chisholm Jr.", "age": 25, "team": "NYY", "position": "CF", "salary": 6200000, "war": 2.9, "ops": 0.786, "obp": 0.326, "slg": 0.460, "hr": 24, "rbi": 61, "stolen_bases": 22},
    {"name": "Anthony Santander", "age": 29, "team": "BAL", "position": "RF", "salary": 7000000, "war": 2.7, "ops": 0.822, "obp": 0.329, "slg": 0.493, "hr": 44, "rbi": 102, "stolen_bases": 3},
    {"name": "Wander Franco", "age": 23, "team": "TB", "position": "SS", "salary": 2000000, "war": 0.5, "ops": 0.740, "obp": 0.323, "slg": 0.417, "hr": 8, "rbi": 40, "stolen_bases": 5},
    {"name": "Spencer Steer", "age": 26, "team": "CIN", "position": "3B", "salary": 720000, "war": 3.6, "ops": 0.831, "obp": 0.353, "slg": 0.478, "hr": 23, "rbi": 77, "stolen_bases": 10},
    {"name": "Jonah Heim", "age": 28, "team": "TEX", "position": "C", "salary": 2600000, "war": 2.8, "ops": 0.731, "obp": 0.308, "slg": 0.423, "hr": 18, "rbi": 55, "stolen_bases": 2},
    {"name": "Josh Jung", "age": 26, "team": "TEX", "position": "3B", "salary": 720000, "war": 2.1, "ops": 0.808, "obp": 0.330, "slg": 0.478, "hr": 23, "rbi": 76, "stolen_bases": 3},
    {"name": "Cedric Mullins", "age": 29, "team": "BAL", "position": "CF", "salary": 5100000, "war": 2.0, "ops": 0.727, "obp": 0.317, "slg": 0.410, "hr": 16, "rbi": 59, "stolen_bases": 24},
    {"name": "Bryan Reynolds", "age": 29, "team": "PIT", "position": "CF", "salary": 13500000, "war": 3.5, "ops": 0.842, "obp": 0.371, "slg": 0.471, "hr": 24, "rbi": 88, "stolen_bases": 6},
    {"name": "Michael Brantley", "age": 36, "team": "HOU", "position": "LF", "salary": 12000000, "war": 1.2, "ops": 0.741, "obp": 0.342, "slg": 0.399, "hr": 6, "rbi": 44, "stolen_bases": 1},
    {"name": "Daulton Varsho", "age": 27, "team": "TOR", "position": "CF", "salary": 4000000, "war": 3.2, "ops": 0.762, "obp": 0.331, "slg": 0.431, "hr": 22, "rbi": 78, "stolen_bases": 16},
    {"name": "Masataka Yoshida", "age": 31, "team": "BOS", "position": "LF", "salary": 26000000, "war": 2.4, "ops": 0.835, "obp": 0.389, "slg": 0.446, "hr": 15, "rbi": 72, "stolen_bases": 0},
    {"name": "Rafael Devers", "age": 27, "team": "BOS", "position": "3B", "salary": 31250000, "war": 3.6, "ops": 0.869, "obp": 0.352, "slg": 0.517, "hr": 33, "rbi": 106, "stolen_bases": 2},
    {"name": "Xander Bogaerts", "age": 31, "team": "SD", "position": "SS", "salary": 20000000, "war": 2.8, "ops": 0.791, "obp": 0.354, "slg": 0.437, "hr": 18, "rbi": 73, "stolen_bases": 4},
    {"name": "Fernando Tatis Jr.", "age": 25, "team": "SD", "position": "RF", "salary": 34800000, "war": 4.2, "ops": 0.874, "obp": 0.349, "slg": 0.525, "hr": 42, "rbi": 97, "stolen_bases": 29},
    {"name": "Ha-Seong Kim", "age": 28, "team": "SD", "position": "SS", "salary": 7000000, "war": 4.5, "ops": 0.789, "obp": 0.351, "slg": 0.438, "hr": 17, "rbi": 60, "stolen_bases": 38},
    {"name": "Jake Cronenworth", "age": 30, "team": "SD", "position": "2B", "salary": 6750000, "war": 2.5, "ops": 0.741, "obp": 0.333, "slg": 0.408, "hr": 17, "rbi": 72, "stolen_bases": 5},
    {"name": "Jackson Holliday", "age": 20, "team": "BAL", "position": "2B", "salary": 720000, "war": 1.5, "ops": 0.703, "obp": 0.324, "slg": 0.379, "hr": 7, "rbi": 33, "stolen_bases": 4},
    {"name": "CJ Abrams", "age": 23, "team": "WSH", "position": "SS", "salary": 720000, "war": 2.9, "ops": 0.739, "obp": 0.311, "slg": 0.428, "hr": 18, "rbi": 61, "stolen_bases": 36},
    {"name": "Max Muncy", "age": 33, "team": "LAD", "position": "3B", "salary": 13500000, "war": 2.3, "ops": 0.820, "obp": 0.378, "slg": 0.442, "hr": 21, "rbi": 68, "stolen_bases": 2},
]


def get_mock_dataframe() -> pd.DataFrame:
    """Return mock player data as a pandas DataFrame."""
    return pd.DataFrame(MOCK_PLAYERS)


class DataImportService:
    """
    Service for importing player data into the database.

    Phase 2 upgrade: Replace `import_mock_data` with `import_from_mlb_api`
    that fetches from https://statsapi.mlb.com/api/v1/people
    """

    def __init__(self, db: Session):
        self.db = db

    def import_mock_data(self) -> dict:
        """Import mock player data. Returns import summary."""
        df = get_mock_dataframe()
        players_created = 0
        players_skipped = 0

        for _, row in df.iterrows():
            existing = self.db.query(Player).filter(Player.name == row["name"]).first()
            if existing:
                players_skipped += 1
                continue

            player = Player(
                name=row["name"],
                age=int(row["age"]),
                team=row["team"],
                position=row["position"],
                salary=float(row["salary"]),
                war=float(row["war"]),
                ops=float(row["ops"]),
                obp=float(row["obp"]),
                slg=float(row["slg"]),
                hr=int(row["hr"]),
                rbi=int(row["rbi"]),
                stolen_bases=int(row["stolen_bases"]),
            )
            self.db.add(player)
            players_created += 1

        self.db.commit()
        return {
            "created": players_created,
            "skipped": players_skipped,
            "total": players_created + players_skipped,
        }

    def import_from_mlb_api(self, season: int = 2024) -> dict:
        """
        Phase 2 placeholder: Fetch live data from MLB Stats API.
        Replace this method body with real API calls.
        """
        raise NotImplementedError("MLB API integration coming in Phase 2")
