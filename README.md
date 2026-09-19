# Redfin Housing Market ELT Pipeline

An end-to-end data pipeline that extracts weekly U.S. metro-level housing market
data from Redfin, loads it into BigQuery, transforms it with dbt, and orchestrates
the whole process with Airflow.

**Question this project answers:** How have home prices trended, metro by metro,
over time?

## Architecture


The full flow is orchestrated by an Airflow DAG with four tasks:

download_redfin_data → load_to_bigquery → run_dbt → test_dbt

## Stack

- **Source:** [Redfin Data Center](https://www.redfin.com/news/data-center/) — weekly metro-level housing data, rolling 4-week windows
- **Ingestion:** Python (pandas)
- **Warehouse:** BigQuery
- **Transformation:** dbt
- **Orchestration:** Airflow (via Astronomer's Astro CLI, running locally in Docker)
- **Visualization:** Looker Studio

## Project structure

dbt/ → dbt project (staging, intermediate, and mart models)
airflow/ → Airflow project (DAG, Docker setup)
notebooks/ → exploratory data analysis, done before building the pipeline


Note: the `dbt/` project is duplicated inside `airflow/include/dbt/` so the
Airflow container has access to it. A cleaner setup would mount the top-level
`dbt/` folder into the container instead of duplicating it — noted here as a
known simplification, not an oversight.

## Data model

- **Grain:** one row per metro area per week (rolling 4-week window ending on `period_end`)
- **Primary key:** `region_id` + `period_end`
- **raw** → untouched mirror of Redfin's source file, all columns retained
- **staging** (`stg_redfin_metro_weekly`) → renamed/typed columns, NSA-only metrics kept
- **intermediate** (`int_redfin_yoy_price_change`) → year-over-year price change per metro, calculated via a date-based self-join (rather than a row-offset `LAG()`) so the comparison is robust to any gaps in the weekly data
- **mart** (`mart_metro_price_trends`) → final table: price, price/sqft, YoY change, plus supply/demand context (active listings, pending sales)

## Key design decisions

- **NSA over SA metrics:** kept not-seasonally-adjusted figures rather than
  Redfin's seasonally-adjusted versions, since NSA is more directly explainable
  and doesn't rely on an opaque adjustment methodology.
- **Full history retained in raw, filtered later:** the raw table holds all
  history Redfin provides; any date filtering happens in staging/marts, not
  at ingestion, so historical scope can change without re-running the extract.
- **Data restatement is expected, not a bug:** Redfin's rolling 4-week windows
  get revised as more sales data comes in. I confirmed this directly — a
  recalculated YoY figure briefly diverged from Redfin's own published YoY
  after a re-download, and matched again once the raw table was refreshed
  from the same snapshot. The pipeline reloads on a schedule rather than
  tracking every historical revision, which was a deliberate scope decision.
- **Nulls in `median_sale_price_nsa` are legitimate:** very low-volume metros
  can have zero reported home sales in a given window, so no median price is
  available. This is expected data sparsity, not a quality defect, so it's
  intentionally excluded from `not_null` testing (documented via investigation,
  not assumption — confirmed the null rows all had null `homes_sold_nsa` too).
- **Local auth via personal ADC credentials, not a service account:** was unable to create a GCP service account key. For local development, the
  existing personal OAuth credential is copied into the container and referenced
  via `GOOGLE_APPLICATION_CREDENTIALS`. A real deployment would use a service
  account or workload identity instead.
- **`dbt run` and `dbt test` are separate Airflow tasks**, not one combined step,
  so a test failure is visible as a distinct, identifiable failure point rather
  than being bundled with the transformation step.

## Running it

```bash
cd airflow
astro dev start
```

Airflow UI: http://localhost:8080 (or whatever port Astro assigns)