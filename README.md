# French Fuel Prices Data Platform

Daily ELT pipeline that ingests French open data on fuel prices,
validates it, and models it into a star schema for analysis.

## Architecture
diagram image: source, Bronze, Silver, dbt on DuckDB, Airflow

## Run it
1. docker compose up --build
2. Open http://localhost:8080 and trigger the DAG fuel_prices_daily
3. Or run each step by hand (commands from Steps 2 to 4)

## Design decisions
- Idempotent loads: output paths depend only on the run date, so a rerun replaces data instead of duplicating it.
- Validation in Silver: rejected rows are counted in a JSON report.
- dbt tests guard Gold: keys, relationships, accepted values, price range.
- DuckDB: no server to run, and the same dbt models can target a cloud warehouse.
- Known limit: the live feed is a snapshot, so history comes from the yearly archive.

## Results
- 30954 rows processed, 0 rejected, 15 dbt tests passing, pipeline runs in 22 seconds

## Next steps
- Spark if volumes grow, object storage such as S3, alerting on failed runs