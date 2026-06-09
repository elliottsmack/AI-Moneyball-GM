# AI Moneyball GM

A production-quality baseball analytics platform built with FastAPI + React + SQLite.

## Architecture Overview

```
ai-moneyball-gm/
├── backend/               # FastAPI Python backend
│   ├── main.py            # Application entry point, startup, CORS
│   ├── database/
│   │   ├── db.py          # SQLAlchemy engine, session factory
│   │   └── models.py      # ORM models (Player)
│   ├── services/
│   │   ├── data_import.py # Data import layer (mock → MLB API in Phase 2)
│   │   └── player_service.py  # Business logic, value scoring
│   └── routers/
│       ├── players.py     # GET /players, /players/{id}, /players/undervalued
│       ├── teams.py       # GET /teams, /teams/positions
│       └── health.py      # GET /health
├── frontend/              # React + TypeScript + Tailwind CSS (Vite)
│   └── src/
│       ├── App.tsx        # Root layout + tab navigation
│       ├── types/         # TypeScript interfaces
│       ├── services/api.ts  # Axios API client
│       ├── components/    # Reusable UI (StatCard, PlayerTable, etc.)
│       └── pages/         # Dashboard, PlayerBrowser, Undervalued
├── database/              # SQLite database files (auto-created)
└── README.md
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | DB status, player count, aggregate stats |
| GET | `/players` | Paginated player list with search/filter/sort |
| GET | `/players/{id}` | Single player by ID |
| GET | `/players/undervalued` | Top N players by value score |
| GET | `/teams` | All unique team abbreviations |
| GET | `/teams/positions` | All unique positions |

### Query Parameters — `GET /players`

| Param | Type | Description |
|-------|------|-------------|
| `search` | string | Filter by name (case-insensitive) |
| `position` | string | Exact position match (e.g. `SS`, `CF`) |
| `team` | string | Exact team abbreviation (e.g. `NYY`) |
| `sort_by` | string | `war`, `salary`, `ops`, `age`, `hr`, `rbi` |
| `sort_dir` | string | `asc` or `desc` |
| `skip` | int | Pagination offset |
| `limit` | int | Max results (1–500) |

## Running Locally

### Backend (port 8000)
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (port 5000)
```bash
cd frontend && npm run dev
```

API docs: `http://localhost:8000/docs`

## Player Data Model

| Field | Type | Description |
|-------|------|-------------|
| `player_id` | int | Auto-incremented primary key |
| `name` | str | Full player name |
| `age` | int | Current age |
| `team` | str | Team abbreviation |
| `position` | str | Primary position |
| `salary` | float | Annual salary in USD |
| `war` | float | Wins Above Replacement |
| `ops` | float | On-base Plus Slugging |
| `obp` | float | On-Base Percentage |
| `slg` | float | Slugging Percentage |
| `hr` | int | Home Runs |
| `rbi` | int | Runs Batted In |
| `stolen_bases` | int | Stolen Bases |

## Value Scoring (Phase 1)

```python
value_score = WAR / (salary / 1_000_000)
```

Higher = more production per dollar. Designed for ML replacement in Phase 3.

## Machine Learning Roadmap

### Phase 2 — MLB API Integration
Replace `DataImportService.import_mock_data()` with `import_from_mlb_api()` using MLB Stats API and FanGraphs.

### Phase 3 — ML Player Valuation
Replace `compute_value_score()` in `player_service.py` with an XGBoost/LightGBM model trained on 10+ seasons. Features: age curves, park factors, platoon splits, injury history.

### Phase 4 — Roster Builder
Custom 20-player roster under a salary cap. Knapsack optimization for positional balance.

### Phase 5 — Win Prediction Engine
Map roster composite WAR → win% using Pythagorean expectation + run environment modeling.

### Phase 6 — Multi-Season Simulation
Monte Carlo simulation over aging curves and contract years for multi-year projections.
