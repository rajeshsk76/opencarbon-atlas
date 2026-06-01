#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "norway"


def main() -> int:
    required = [
        "plants.csv",
        "locations.csv",
        "emissions.csv",
        "products.csv",
        "point_sources.csv",
        "capture_status.csv",
        "energy.csv",
        "logistics.csv",
        "references.csv",
        "data_quality.csv",
    ]
    missing = [file_name for file_name in required if not (DATA_DIR / file_name).exists()]
    if missing:
        print(f"Missing seed files: {', '.join(missing)}")
        return 1
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_geojson.py")], check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_data.py")], check=True)
    print("Sample data is present and validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

