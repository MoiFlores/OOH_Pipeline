locals {
  bucket_object_arns = [for arn in var.bucket_arns : "${arn}/*"]
}

data "aws_iam_policy_document" "emr_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["emr-serverless.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "emr_job_role" {
  name               = "${var.name_prefix}-emr-job-role"
  assume_role_policy = data.aws_iam_policy_document.emr_assume_role.json
  tags               = var.tags
}


data "aws_iam_policy_document" "emr_s3_access" {
  statement {
    actions   = ["s3:ListBucket", "s3:GetBucketLocation"]
    resources = var.bucket_arns
  }
  statement {
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]
    resources = local.bucket_object_arns
  }
}

resource "aws_iam_policy" "emr_s3_policy" {
  name   = "${var.name_prefix}-emr-s3-policy"
  policy = data.aws_iam_policy_document.emr_s3_access.json
}

resource "aws_iam_role_policy_attachment" "emr_attach" {
  role       = aws_iam_role.emr_job_role.name
  policy_arn = aws_iam_policy.emr_s3_policy.arn
}

data "aws_iam_policy_document" "mwaa_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["airflow.amazonaws.com", "airflow-env.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "mwaa_execution_role" {
  name               = "${var.name_prefix}-mwaa-execution-role"
  assume_role_policy = data.aws_iam_policy_document.mwaa_assume_role.json
  tags               = var.tags
}

data "aws_iam_policy_document" "mwaa_execution_policy_doc" {
  statement {
    sid       = "AirflowMetrics"
    effect    = "Allow"
    actions   = ["airflow:PublishMetrics"]
    resources = ["arn:aws:airflow:${var.region}:${var.account_id}:environment/${var.name_prefix}-mwaa"]
  }

  statement {
    sid    = "CloudWatchLogs"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:GetLogEvents",
      "logs:GetLogRecord",
      "logs:GetLogGroupFields",
      "logs:GetQueryResults"
    ]
    resources = [
      "arn:aws:logs:${var.region}:${var.account_id}:log-group:airflow-${var.name_prefix}-mwaa-*"
    ]
  }

  statement {
    sid       = "ReadDagBucket"
    effect    = "Allow"
    actions   = ["s3:ListBucket"]
    resources = [var.dags_bucket_arn]
  }

  statement {
    sid     = "ReadDagObjects"
    effect  = "Allow"
    actions = ["s3:GetObject", "s3:GetObjectVersion"]
    resources = [
      "${var.dags_bucket_arn}/dags/*",
      "${var.dags_bucket_arn}/plugins/*",
      "${var.dags_bucket_arn}/requirements/*",
      "${var.dags_bucket_arn}/startup/*"
    ]
  }

  statement {
    sid    = "CeleryQueueAccess"
    effect = "Allow"
    actions = [
      "sqs:ChangeMessageVisibility",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:GetQueueUrl",
      "sqs:ReceiveMessage",
      "sqs:SendMessage"
    ]
    resources = ["arn:aws:sqs:${var.region}:${var.account_id}:airflow-celery-*"]
  }
}

resource "aws_iam_policy" "mwaa_execution_policy" {
  name   = "${var.name_prefix}-mwaa-execution-policy"
  policy = data.aws_iam_policy_document.mwaa_execution_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "mwaa_execution_attach" {
  role       = aws_iam_role.mwaa_execution_role.name
  policy_arn = aws_iam_policy.mwaa_execution_policy.arn
}