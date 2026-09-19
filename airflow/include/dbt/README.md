# dbt transformations for the Redfin pipeline

Staging → intermediate → mart models transforming raw Redfin housing data
into a metro-level price trends table.

See the [top-level README](../README.md) for full project details, architecture,
and design decisions.

## Run locally

```bash
dbt run
dbt test
```