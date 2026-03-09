# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI backend for highway traffic monitoring, analysis, and LSTM-based prediction. Uses PostgreSQL with PostGIS for geospatial data, asyncpg for async database access, and TensorFlow/Keras for traffic flow prediction.

## Commands

### Run the application
```shell
python main.py
```
Starts uvicorn with hot-reload on the port specified in `.env` (default 8000).

### Install dependencies
```shell
./scripts/install.sh
```
Uses pip with `requirements.txt`. The project also has a `pyproject.toml` managed by `uv`.

### Initialize database
```shell
# Start PostGIS container (for local dev):
./scripts/run_pg.sh

# Create tables:
python scripts/init_db.py
```

### Seed data from CSV/Excel
Scripts in `scripts/data-to-db/` import traffic data into PostgreSQL (gantry, trunk_road, ramp, road_condition, road_coordinate).

### Deploy
Push to `main` triggers GitHub Actions CI/CD which SSHs into the server and runs `./run.sh`.

## Architecture

### Layered structure
- **`router/`** — FastAPI route handlers. Each file exports a `router` (APIRouter). All routers are auto-discovered and registered by `load_routers()` in `core/utils.py` — just add a new `.py` file with a `router` variable.
- **`db/`** — Repository layer with raw SQL queries via asyncpg. Functions use the `@with_connection` decorator from `db/core.py` which auto-acquires a connection from the pool (or reuses one passed via `conn` kwarg).
- **`db/models.py`** — Dataclass models with `from_db(record)` static methods to convert asyncpg Records to Python objects, and `to_schema()` methods for API serialization.
- **`schemas/`** — Pydantic models for request/response validation. The generic `Response[T]` wrapper in `schemas/common.py` is the standard API response envelope.
- **`core/`** — Config (`env.py` reads `.env` via python-dotenv), logging (`log.py` writes to `log_file.log`), middleware (CORS), and `load_routers` utility.
- **`lstm/`** — LSTM prediction module. `predict.py` loads `traffic_model.h5` at import time, takes 6 time-step inputs (5-min intervals), and predicts the next 6 intervals (30 minutes).

### Key patterns
- **Response helpers**: Use `Ok(data)`, `Bad(msg)`, `NotFound()` from `router/response.py` — these return dicts matching the `Response` schema (`{code, data, msg}`).
- **Database connections**: Use `@with_connection` decorator on db functions. First parameter must be `conn`. Supports passing an existing connection via `conn=` kwarg for transaction reuse.
- **Transactions**: Use `async with atomic() as conn:` context manager from `db/core.py`, then pass `conn=conn` to decorated functions.
- **Road link_id**: `link_id` is a large integer that loses precision in JavaScript. Always convert to string when sending to frontend (`str(self.link_id)`).
- **PostGIS geometry**: Road geometries stored as `GEOMETRY(LINESTRING, 4326)`, parsed with `shapely.wkb.loads(record["road_geom"], hex=True)`. Gantry locations use a generated `GEOMETRY(POINT, 4326)` column.

### Database
PostgreSQL with PostGIS. Key tables: `road`, `gantry`, `vehicle_passage`, `road_condition`, `trunk_road_flow`, `ramp_flow`, `gantry_traffic_flow`. Schema defined in `sql/init.sql`.

## Environment Variables

Copy `.env.example` to `.env` and fill in:
- `PORT` — server port
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` — PostgreSQL connection

## Development Conventions

- All I/O operations must use `async/await`.
- Use PEP 484 type hints throughout.
- Use the logger from `core.log` (not print statements).
- Python 3.12+ required.
