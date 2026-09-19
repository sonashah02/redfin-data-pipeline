from airflow.sdk import dag, task
from pendulum import datetime

@dag(
    start_date=datetime(2026, 1, 1),
    schedule="@weekly",
    tags=["redfin"],
)
def redfin_pipeline():

    @task
    def download_redfin_data():
        import pandas as pd

        url = 'https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_data_center/housing_market/weekly/all_metros.csv'
        raw_data = pd.read_csv(url)

        raw_data.columns = (
            raw_data.columns
            .str.strip()
            .str.lower()
            .str.replace(r'[^\w\s]', '', regex=True)
            .str.replace(r'\s+', '_', regex=True)
        )

        raw_data.to_csv('/tmp/redfin_all_metros.csv', index=False)

    @task
    def load_to_bigquery():
        import os
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/usr/local/airflow/include/gcp_credentials.json'

        from google.cloud import bigquery

        client = bigquery.Client(project="project-93ae46fe-b485-4962-b2c")

        table_id = f"{client.project}.redfin_raw.metro_weekly_housing"

        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
            write_disposition="WRITE_TRUNCATE",
        )

        with open("/tmp/redfin_all_metros.csv", "rb") as source_file:
            load_job = client.load_table_from_file(source_file, table_id, job_config=job_config)

        load_job.result()

        table = client.get_table(table_id)
        print(f"Loaded {table.num_rows} rows into {table_id}")

    @task
    def run_dbt():
        import subprocess
        import os

        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/usr/local/airflow/include/gcp_credentials.json'

        result = subprocess.run(
            ["dbt", "run", "--project-dir", "/usr/local/airflow/include/dbt", "--profiles-dir",
             "/usr/local/airflow/include/dbt"],
            capture_output=True,
            text=True,
        )

        print(result.stdout)
        print(result.stderr)

        if result.returncode != 0:
            raise Exception(f"dbt run failed:\n{result.stdout}\n{result.stderr}")

    @task
    def test_dbt():
        import subprocess
        import os

        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/usr/local/airflow/include/gcp_credentials.json'

        result = subprocess.run(
            ["dbt", "test", "--project-dir", "/usr/local/airflow/include/dbt", "--profiles-dir",
             "/usr/local/airflow/include/dbt"],
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        print(result.stderr)
        if result.returncode != 0:
            raise Exception(f"dbt test failed:\n{result.stdout}\n{result.stderr}")

    download_redfin_data() >> load_to_bigquery() >> run_dbt() >> test_dbt()


redfin_pipeline()