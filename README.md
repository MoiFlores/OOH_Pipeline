# OOH Pipeline

## Project Overview

This project implements an end-to-end data pipeline for the OOH Data Engineer Challenge using Python and PySpark.  
The pipeline ingests raw transaction and merchant data, applies required cleaning rules, and publishes analytical outputs to Gold datasets for Q1 to Q5 of the challenge.

The implementation is designed to balance production thinking:

- Production-style cloud architecture in Terraform
- Cost-aware execution strategy
- Clear orchestration flow with Airflow
- Reproducible analytics outputs for reporting

## Architecture Decision

The selected approach is a hybrid model:

- **Infrastructure definition:** Terraform modules for S3, IAM, EMR Serverless, Glue, Athena, and optional MWAA, Airflow setup for the local environment.
- **Processing engine:** PySpark jobs executed through EMR Serverless for cost saving and interview showcase.
- **Storage model:** DataLake and Medallion Architecture: Bronze, Silver, and Gold zones in S3.

## Data Flow

1. Raw files are uploaded to S3 Bronze. For this showcase the files are being uploaded using `scripts/upload_to_s3.py` having the input files in the root of the folder.
2. Ingestion job applies required cleaning and writes curated Bronze output. Right now the ingestion mode is overwrite, but it has the potential to convert it into an incremental approach.
3. Transformation job standardizes fields and writes Silver.
4. Analytics job produces Q1 to Q5 outputs in Gold.
5. Athena can query Gold outputs for validation and report extraction.

## Repository Structure

```text
OOH_Pipeline/
├── terraform/
├── src/
│   ├── common/
│   └── jobs/
├── dags/
├── docker/
├── scripts/
├── docs/
│   └── report.md
└── requirements.txt
```

## Setup

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Provision infrastructure

```bash
cd terraform
terraform init
terraform workspace select dev
terraform apply -var-file=environments/dev/terraform.tfvars
```

### 3) Upload input data and code artifacts

```bash
python scripts/upload_to_s3.py --bronze-bucket <bronze-bucket-name> --upload-code --code-prefix code
```

### 4) Start Airflow

```bash
cd docker
docker compose up --build
```

Airflow UI: `http://localhost:8080`  
Default credentials: `admin` / `admin`

### 5) Run the DAG

Trigger `ooh_pipeline` from Airflow UI and monitor task states:

- `ingestion_submit`
- `transformation_submit`
- `analytics_submit`

## Outputs

Gold outputs are written to:

- `q1/`
- `q2/`
- `q3/`
- `q4/`
- `q5/`

These datasets support the final report in `docs/report.md`.

## Notes:

- MWAA Terraform is included to demonstrate production deployment capability.
- Local Airflow is used for orchestration during the demo to avoid unnecessary cost.
- DAG logic is structured to remain compatible with cloud orchestration patterns.

## Cost and Teardown

After collecting results and evidence:

```bash
cd terraform
terraform destroy -var-file=environments/dev/terraform.tfvars
```

If you need to keep outputs for reporting, archive Gold data before teardown.
