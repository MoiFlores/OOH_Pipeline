import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.jobs.analytics import run


def main() -> None:
    parser = argparse.ArgumentParser(description="Run analytics job.")
    parser.add_argument("silver_path")
    parser.add_argument("gold_base_path")
    args = parser.parse_args()
    run(args.silver_path, args.gold_base_path)


if __name__ == "__main__":
    main()
