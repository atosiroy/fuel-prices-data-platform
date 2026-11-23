# French Fuel Prices Data Platform

[![CI](https://github.com/atosiroy/fuel-prices-data-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/atosiroy/fuel-prices-data-platform/actions/workflows/ci.yml)

Daily ELT pipeline that ingests French open data on fuel prices, validates it, and models it into a star schema with dbt, DuckDB and Airflow.

## Architecture

```
data.gouv.fr (XML zip)
        │
        ▼
ingestion/ingest.py        Bronze: raw zip, one folder per date
        │
        ▼
transform/silver.py        Silver: parsed, typed, validated Parquet + validation.json
        │
        ▼
dbt (DuckDB)               stg_prices → dim_stations, dim_fuel_type → fact_prices → mart
        │
        ▼
Airflow DAG (Docker)       ingest_bronze → build_silver → dbt_run → dbt_test
```

## Data model

| Model | Type | Grain |
| --- | --- | --- |
| `stg_prices` | view | one row per station, fuel and price update (cleaned Silver) |
| `dim_stations` | table | one row per station (latest known version) |
| `dim_fuel_type` | table | one row per fuel type |
| `fact_prices` | table | one row per station, fuel and price timestamp |
| `mart_avg_price_department_week` | table | average price by department, fuel and week |

## Design decisions

- **Idempotent loads.** Output paths depend only on the run date. Rerunning a date overwrites its partition instead of duplicating rows.
- **Validation in Silver.** Missing values, out-of-range prices and duplicates are counted and written to `validation.json`, so data quality is measurable on every run.
- **Tests guard the warehouse.** dbt tests check keys (`unique`, `not_null`), relationships between facts and dimensions, accepted fuel ids, and a price range rule.
- **DuckDB as the warehouse.** No server to run, and the dbt models could target a cloud warehouse with a different profile.
- **Known limits.** The live feed is a snapshot of current prices, so history comes from the yearly archive. Corsican postal codes start with `20`, so the department field does not distinguish `2A` and `2B`.

## Results

Run date: `[2026-11-23]`

| Metric | Value | Source |
| --- | --- | --- |
| Rows ingested (`rows_in`) | 32771 | `data/reports/date=…/validation.json` |
| Rows rejected | 0 | same file |
| Duplicates removed | 0 | same file |
| Rows kept (`rows_out`) | 32771 | same file |
| dbt data tests passing | 15 | `dbt test` summary |
| Pipeline runtime | 12.81 s | Airflow Graph view |
| CI | passing | GitHub Actions |

## Run it

### With Docker and Airflow

```bash
docker compose up --build
```

Open http://localhost:8080, sign in as `admin` (password in the container logs: `docker compose logs airflow | grep -i password`), enable `fuel_prices_daily`, and trigger it.

### By hand

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m ingestion.ingest --date 2026-11-23
python -m transform.silver --date 2026-11-23
dbt build --project-dir dbt_project --profiles-dir dbt_project
dbt test --project-dir dbt_project --profiles-dir dbt_project
```

## Tests and lint

```bash
ruff check .
pytest -q
```

GitHub Actions runs both on every push, then builds the Silver layer from `tests/fixtures/sample.xml` and runs `dbt build`.

## Project structure

```
ingestion/          download raw file to Bronze
transform/          parse and validate XML into Silver Parquet
dbt_project/        dbt models, tests and profile
dags/               Airflow DAG
tests/              pytest tests and a 20-station XML fixture
.github/workflows/  CI definition
```

## Source

Fuel prices from the French Ministry of Economy's open data, published on data.gouv.fr. Check the dataset's licence before reuse.
