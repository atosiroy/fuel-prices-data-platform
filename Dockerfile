FROM apache/airflow:2.10.5-python3.11

USER root
RUN python -m venv /opt/dbt-venv
RUN /opt/dbt-venv/bin/pip install --no-cache-dir dbt-duckdb
RUN chown -R airflow /opt/dbt-venv

USER airflow
RUN pip install --no-cache-dir requests pandas pyarrow duckdb
