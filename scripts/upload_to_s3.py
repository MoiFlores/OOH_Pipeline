import argparse
import pathlib
import sys
import tempfile
import zipfile

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def upload_file(s3_client, local_path: pathlib.Path, bucket: str, key: str) -> None:
    print(f"Uploading {local_path} -> s3://{bucket}/{key}")
    s3_client.upload_file(str(local_path), bucket, key)


def upload_directory_recursive(
    s3_client, local_dir: pathlib.Path, bucket: str, s3_prefix: str
) -> None:
    for file_path in local_dir.rglob("*"):
        if file_path.is_file():
            relative = file_path.relative_to(local_dir).as_posix()
            key = f"{s3_prefix.rstrip('/')}/{relative}"
            upload_file(s3_client, file_path, bucket, key)


def build_src_zip(src_dir: pathlib.Path) -> pathlib.Path:
    temp_dir = pathlib.Path(tempfile.mkdtemp(prefix="ooh_src_zip_"))
    zip_path = temp_dir / "src.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in src_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(src_dir.parent).as_posix()
                zf.write(file_path, arcname)
    return zip_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload OOH challenge input files to S3 Bronze.")
    parser.add_argument("--bronze-bucket", required=True, help="Target Bronze S3 bucket name")
    parser.add_argument("--region", default="us-east-1", help="AWS region (default: us-east-1)")
    parser.add_argument("--prefix", default="raw", help="S3 prefix under bucket (default: raw)")
    parser.add_argument(
        "--code-prefix",
        default="code",
        help="S3 prefix where src/ tree is uploaded for EMR jobs (default: code)",
    )
    parser.add_argument(
        "--upload-code",
        action="store_true",
        help="Upload src/ tree to S3 for EMR Serverless entrypoints",
    )
    parser.add_argument(
        "--transactions-file",
        default="part-00000-tid-860771939793626614-979f966a-6d53-4896-9692-f81194d27b99-109986-1-c000.snappy.parquet",
        help="Path to transactions parquet file"
    )
    parser.add_argument(
        "--merchants-file",
        default="merchants-subset.csv",
        help="Path to merchants CSV file"
    )
    args = parser.parse_args()

    repo_root = pathlib.Path(__file__).resolve().parents[1]
    transactions_path = (repo_root / args.transactions_file).resolve()
    merchants_path = (repo_root / args.merchants_file).resolve()
    src_path = (repo_root / "src").resolve()

    if not transactions_path.exists():
        print(f"ERROR: transactions file not found: {transactions_path}")
        return 1
    if not merchants_path.exists():
        print(f"ERROR: merchants file not found: {merchants_path}")
        return 1
    if args.upload_code and not src_path.exists():
        print(f"ERROR: src directory not found: {src_path}")
        return 1

    s3 = boto3.client("s3", region_name=args.region)
    prefix = args.prefix.strip("/")
    code_prefix = args.code_prefix.strip("/")

    try:
        upload_file(
            s3,
            transactions_path,
            args.bronze_bucket,
            f"{prefix}/historical_transactions/{transactions_path.name}",
        )
        upload_file(
            s3,
            merchants_path,
            args.bronze_bucket,
            f"{prefix}/merchants/{merchants_path.name}",
        )
        if args.upload_code:
            upload_directory_recursive(
                s3,
                src_path,
                args.bronze_bucket,
                f"{code_prefix}/src",
            )
            src_zip = build_src_zip(src_path)
            upload_file(
                s3,
                src_zip,
                args.bronze_bucket,
                f"{code_prefix}/src.zip",
            )
    except (BotoCoreError, ClientError) as exc:
        print(f"Upload failed: {exc}")
        return 1

    print("Upload complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())