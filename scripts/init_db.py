from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import settings
from app.db.session import ensure_database_ready


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize and seed the Vietnam Mineral Map SQLite/SQLAlchemy database."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear existing rows and re-import everything from khoang_san_viet_nam_tinh.sql",
    )
    args = parser.parse_args()

    counts = ensure_database_ready(reset=args.reset)
    print(f"Database ready: {settings.database_url}")
    print(f"Seeded from:    {settings.resolved_seed_sql_path}")
    for table, count in counts.items():
        print(f"  - {table}: {count} rows")


if __name__ == "__main__":
    main()
