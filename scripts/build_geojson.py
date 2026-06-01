#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "norway"


def read_csv(file_name: str) -> list[dict[str, str]]:
    with (DATA_DIR / file_name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_geojson() -> dict[str, object]:
    plants = {row["plant_id"]: row for row in read_csv("plants.csv")}
    features = []
    for location in read_csv("locations.csv"):
        plant = plants[location["plant_id"]]
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(location["longitude"]), float(location["latitude"])],
                },
                "properties": {
                    "plant_id": plant["plant_id"],
                    "name": plant["name"],
                    "operator": plant["operator"],
                    "sector": plant["sector"],
                    "municipality": plant["municipality"],
                    "county": plant["county"],
                    "status": plant["status"],
                    "primary_product": plant["primary_product"],
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}


def main() -> int:
    geojson = build_geojson()
    with (DATA_DIR / "locations.geojson").open("w", encoding="utf-8") as handle:
        json.dump(geojson, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print("Wrote data/norway/locations.geojson")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

