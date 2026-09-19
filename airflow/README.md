# Airflow orchestration for the Redfin pipeline

Runs the four-task DAG that downloads Redfin's weekly metro housing data,
loads it into BigQuery, and triggers the dbt transformations.

See the [top-level README](../README.md) for full project details, architecture,
and design decisions.

## Run locally

```bash
astro dev start
```

Airflow UI: http://localhost:8080 (or whatever port Astro assigns)