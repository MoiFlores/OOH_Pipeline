from datetime import datetime
import os

from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.operators.bash import BashOperator
from airflow.providers.amazon.aws.operators.emr import EmrServerlessStartJobOperator
from airflow.providers.amazon.aws.sensors.emr import EmrServerlessJobSensor

EXECUTION_BACKEND = os.getenv("EXECUTION_BACKEND", "local")  # local or emr
AWS_CONN_ID = os.getenv("AWS_CONN_ID", "aws_default")

EMR_SERVERLESS_APPLICATION_ID = os.getenv("EMR_SERVERLESS_APPLICATION_ID", "")
EMR_SERVERLESS_EXECUTION_ROLE_ARN = os.getenv("EMR_SERVERLESS_EXECUTION_ROLE_ARN", "")
EMR_S3_CODE_PREFIX = os.getenv("EMR_S3_CODE_PREFIX", "")
EMR_PY_FILES = os.getenv("EMR_PY_FILES", f"{EMR_S3_CODE_PREFIX}/src.zip")
BRONZE_URI = os.getenv("BRONZE_URI", "")
SILVER_URI = os.getenv("SILVER_URI", "")
GOLD_URI = os.getenv("GOLD_URI", "")

LOCAL_TRANSACTIONS_PATH = os.getenv("LOCAL_TRANSACTIONS_PATH", "/opt/airflow/data/raw/historical_transactions.parquet")
LOCAL_MERCHANTS_PATH = os.getenv("LOCAL_MERCHANTS_PATH", "/opt/airflow/data/raw/merchants.csv")
LOCAL_BRONZE_PATH = os.getenv("LOCAL_BRONZE_PATH", "/opt/airflow/data/bronze")
LOCAL_SILVER_PATH = os.getenv("LOCAL_SILVER_PATH", "/opt/airflow/data/silver")
LOCAL_GOLD_PATH = os.getenv("LOCAL_GOLD_PATH", "/opt/airflow/data/gold")

with DAG(
    dag_id="ooh_pipeline",
    start_date=datetime(2026, 3, 14),
    schedule_interval="@daily",
    catchup=False,
    tags=["ooh", "pyspark"],
) as dag:
    if EXECUTION_BACKEND == "local":
        ingest = BashOperator(
            task_id="ingestion",
            bash_command=(
                "python /opt/airflow/src/jobs/ingestion_entrypoint.py "
                f"{LOCAL_TRANSACTIONS_PATH} {LOCAL_MERCHANTS_PATH} {LOCAL_BRONZE_PATH}"
            ),
        )
        transform = BashOperator(
            task_id="transformation",
            bash_command=(
                "python /opt/airflow/src/jobs/transformation_entrypoint.py "
                f"{LOCAL_BRONZE_PATH} {LOCAL_SILVER_PATH}"
            ),
        )
        analytics = BashOperator(
            task_id="analytics",
            bash_command=(
                "python /opt/airflow/src/jobs/analytics_entrypoint.py "
                f"{LOCAL_SILVER_PATH} {LOCAL_GOLD_PATH}"
            ),
        )
        ingest >> transform >> analytics
    else:
        required = {
            "EMR_SERVERLESS_APPLICATION_ID": EMR_SERVERLESS_APPLICATION_ID,
            "EMR_SERVERLESS_EXECUTION_ROLE_ARN": EMR_SERVERLESS_EXECUTION_ROLE_ARN,
            "EMR_S3_CODE_PREFIX": EMR_S3_CODE_PREFIX,
            "EMR_PY_FILES": EMR_PY_FILES,
            "BRONZE_URI": BRONZE_URI,
            "SILVER_URI": SILVER_URI,
            "GOLD_URI": GOLD_URI,
        }
        missing = [k for k, v in required.items() if not v.strip()]
        if missing:
            raise AirflowException(
                f"Missing required env vars for EMR backend: {', '.join(sorted(missing))}"
            )

        ingest_submit = EmrServerlessStartJobOperator(
            task_id="ingestion_submit",
            aws_conn_id=AWS_CONN_ID,
            application_id=EMR_SERVERLESS_APPLICATION_ID,
            execution_role_arn=EMR_SERVERLESS_EXECUTION_ROLE_ARN,
            job_driver={
                "sparkSubmit": {
                    "entryPoint": f"{EMR_S3_CODE_PREFIX}/src/jobs/ingestion_entrypoint.py",
                    "entryPointArguments": [
                        f"{BRONZE_URI}/historical_transactions/",
                        f"{BRONZE_URI}/merchants/",
                        f"{BRONZE_URI}/bronze_cleaned/",
                    ],
                    "sparkSubmitParameters": f"--py-files {EMR_PY_FILES}",
                }
            },
        )

        ingest_wait = EmrServerlessJobSensor(
            task_id="ingestion_wait",
            aws_conn_id=AWS_CONN_ID,
            application_id=EMR_SERVERLESS_APPLICATION_ID,
            job_run_id=ingest_submit.output,
            target_states={"SUCCESS"},
        )

        transform_submit = EmrServerlessStartJobOperator(
            task_id="transformation_submit",
            aws_conn_id=AWS_CONN_ID,
            application_id=EMR_SERVERLESS_APPLICATION_ID,
            execution_role_arn=EMR_SERVERLESS_EXECUTION_ROLE_ARN,
            job_driver={
                "sparkSubmit": {
                    "entryPoint": f"{EMR_S3_CODE_PREFIX}/src/jobs/transformation_entrypoint.py",
                    "entryPointArguments": [
                        f"{BRONZE_URI}/bronze_cleaned/",
                        SILVER_URI,
                    ],
                    "sparkSubmitParameters": f"--py-files {EMR_PY_FILES}",
                }
            },
        )

        transform_wait = EmrServerlessJobSensor(
            task_id="transformation_wait",
            aws_conn_id=AWS_CONN_ID,
            application_id=EMR_SERVERLESS_APPLICATION_ID,
            job_run_id=transform_submit.output,
            target_states={"SUCCESS"},
        )

        analytics_submit = EmrServerlessStartJobOperator(
            task_id="analytics_submit",
            aws_conn_id=AWS_CONN_ID,
            application_id=EMR_SERVERLESS_APPLICATION_ID,
            execution_role_arn=EMR_SERVERLESS_EXECUTION_ROLE_ARN,
            job_driver={
                "sparkSubmit": {
                    "entryPoint": f"{EMR_S3_CODE_PREFIX}/src/jobs/analytics_entrypoint.py",
                    "entryPointArguments": [
                        SILVER_URI,
                        GOLD_URI,
                    ],
                    "sparkSubmitParameters": f"--py-files {EMR_PY_FILES}",
                }
            },
        )

        analytics_wait = EmrServerlessJobSensor(
            task_id="analytics_wait",
            aws_conn_id=AWS_CONN_ID,
            application_id=EMR_SERVERLESS_APPLICATION_ID,
            job_run_id=analytics_submit.output,
            target_states={"SUCCESS"},
        )

        ingest_submit >> ingest_wait >> transform_submit >> transform_wait >> analytics_submit >> analytics_wait