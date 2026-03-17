FROM apache/airflow:2.9.3

ARG AIRFLOW_VERSION=2.9.3
ARG PYTHON_VERSION=3.12
ARG CONSTRAINT_URL=https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt

USER airflow

RUN pip install --no-cache-dir \
    "apache-airflow-providers-amazon==8.25.0" \
    --constraint "${CONSTRAINT_URL}"
