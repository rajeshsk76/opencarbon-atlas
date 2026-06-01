from __future__ import annotations

import csv
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data" / "norway"

TABLE_FILES = {
    "plants": "plants.csv",
    "locations": "locations.csv",
    "emissions": "emissions.csv",
    "products": "products.csv",
    "point_sources": "point_sources.csv",
    "capture_status": "capture_status.csv",
    "energy": "energy.csv",
    "logistics": "logistics.csv",
    "references": "references.csv",
    "data_quality": "data_quality.csv",
}

NUMERIC_FIELDS = {
    "latitude",
    "longitude",
    "value",
    "estimated_co2_concentration_pct",
    "annual_co2_tonnes",
    "target_capture_tonnes_per_year",
    "port_distance_km",
}
INTEGER_FIELDS = {"start_year", "year"}
BOOLEAN_FIELDS = {"rail_access"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def coerce(value: str, field: str) -> Any:
    if value == "":
        return None
    if field in NUMERIC_FIELDS:
        return float(value)
    if field in INTEGER_FIELDS:
        return int(value)
    if field in BOOLEAN_FIELDS:
        return value.lower() in {"true", "1", "yes"}
    return value


def coerce_row(row: dict[str, str]) -> dict[str, Any]:
    return {field: coerce(value, field) for field, value in row.items()}


@lru_cache(maxsize=1)
def load_tables() -> dict[str, list[dict[str, Any]]]:
    return {
        table: [coerce_row(row) for row in read_csv(DATA_DIR / file_name)]
        for table, file_name in TABLE_FILES.items()
    }


def rows_for(table: str, plant_id: str) -> list[dict[str, Any]]:
    return [row for row in load_tables()[table] if row.get("plant_id") == plant_id]


def get_plant_detail(plant_id: str) -> dict[str, Any] | None:
    tables = load_tables()
    plant = next((row for row in tables["plants"] if row["plant_id"] == plant_id), None)
    if plant is None:
        return None
    location = next((row for row in tables["locations"] if row["plant_id"] == plant_id), None)
    return {
        "plant": plant,
        "location": location,
        "emissions": rows_for("emissions", plant_id),
        "products": rows_for("products", plant_id),
        "point_sources": rows_for("point_sources", plant_id),
        "capture_status": rows_for("capture_status", plant_id),
        "energy": rows_for("energy", plant_id),
        "logistics": rows_for("logistics", plant_id),
        "data_quality": rows_for("data_quality", plant_id),
    }


def load_geojson() -> dict[str, Any]:
    with (DATA_DIR / "locations.geojson").open(encoding="utf-8") as handle:
        return json.load(handle)
