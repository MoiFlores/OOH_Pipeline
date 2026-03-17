import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.jobs.ingestion import run


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ingestion job.")
    parser.add_argument("transactions_path")
    parser.add_argument("merchants_path")
    parser.add_argument("output_path")
    args = parser.parse_args()
    run(args.transactions_path, args.merchants_path, args.output_path)


if __name__ == "__main__":
    main()
