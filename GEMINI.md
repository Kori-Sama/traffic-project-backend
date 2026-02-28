# Traffic Project Backend - GEMINI.md

## Project Overview
This project is a FastAPI-based backend designed for traffic monitoring, analysis, and prediction. It integrates geographical data (using PostGIS), vehicle passage records from highway gantries, and machine learning models (LSTM) to provide real-time and predictive traffic insights.

### Main Technologies
- **Framework:** FastAPI (Python 3.12+)
- **Database:** PostgreSQL with PostGIS extension (accessed via `asyncpg`)
- **AI/ML:** TensorFlow/Keras (LSTM model for traffic flow prediction), Scikit-learn (MinMaxScaler)
- **Data Processing:** Pandas, NumPy
- **Asynchronous IO:** Anyio, Starlette
- **Deployment:** Uvicorn

### Key Features
- **Traffic Prediction:** Uses an LSTM model (`lstm/traffic_model.h5`) to predict traffic volume for the next 30 minutes in 5-minute intervals.
- **Gantry & Vehicle Tracking:** Manages gantry locations and records vehicle passages for both trunk roads and ramps.
- **Road Condition Monitoring:** Tracks real speed, free-flow speed, and congestion indices for road segments.
- **Static Video Serving:** Serves traffic surveillance videos from the `videos/` directory.
- **Geospatial Analysis:** Leverages PostGIS for handling road geometries and gantry locations.

## Architecture
- `main.py`: Application entry point and router initialization.
- `core/`: Core configurations, environment variable management (`env.py`), logging, and middleware.
- `db/`: Database connection pooling and repository-style access layer.
- `router/`: API endpoints organized by resource (traffic, road, gantry, ramp, etc.).
- `schemas/`: Pydantic models for request/response validation and serialization.
- `lstm/`: Prediction logic, including data preprocessing and model inference.
- `scripts/`: Utility scripts for environment setup, database initialization, and data migration from Excel/CSV to PostgreSQL.
- `data/`: Raw traffic data and processed CSV files used for model training or initial database seeding.
- `sql/`: SQL schema definitions, including PostGIS extension setup.

## Building and Running

### Prerequisites
- Python 3.12+
- PostgreSQL with PostGIS extension

### Environment Setup
1. **Install Dependencies:**
   ```shell
   ./scripts/install.sh
   ```
2. **Configuration:**
   Create a `.env` file in the root directory based on `.env.example`:
   ```env
   PORT=8000
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=your_user
   DB_PASSWORD=your_password
   DB_NAME=traffic_db
   ```

### Database Initialization
1. **Start PostgreSQL** (ensure PostGIS is available).
2. **Run Initialization Script:**
   ```shell
   python scripts/init_db.py
   ```
   This will create the necessary tables and extensions defined in `sql/init.sql`.

### Running the Application
```shell
python main.py
```
The API will be available at `http://localhost:8000` (or the port specified in `.env`).

## Development Conventions
- **Asynchronous Code:** Use `async/await` for all I/O operations (database, network).
- **Database Access:** Use the `@with_connection` decorator from `db/core.py` to handle database connections within repository functions.
- **Routing:** New routers should be placed in the `router/` directory and will be automatically loaded by `load_routers` in `main.py`.
- **Validation:** Always define Pydantic schemas in `schemas/` for any new API endpoints.
- **Logging:** Use the logger from `core.log` for consistent logging.
- **Type Hinting:** Use PEP 484 type hints throughout the codebase.
