#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "norway"

REQUIRED_COLUMNS = {
    "plants.csv": [
        "plant_id",
        "name",
        "operator",
        "sector",
        "municipality",
        "county",
        "status",
        "primary_product",
        "start_year",
        "website",
    ],
    "locations.csv": [
        "location_id",
        "plant_id",
        "latitude",
        "longitude",
        "address",
        "municipality",
        "county",
        "coordinate_precision",
    ],
    "emissions.csv": ["emission_id", "plant_id", "year", "scope", "co2e_tonnes", "source_id"],
    "products.csv": [
        "product_id",
        "plant_id",
        "product",
        "annual_capacity_tonnes",
        "capacity_year",
        "source_id",
    ],
    "point_sources.csv": [
        "point_source_id",
        "plant_id",
        "source_name",
        "stream_type",
        "estimated_co2_concentration_pct",
        "annual_co2_tonnes",
        "capture_priority",
    ],
    "capture_status.csv": [
        "capture_status_id",
        "plant_id",
        "readiness",
        "capture_technology",
        "target_capture_tonnes_per_year",
        "storage_or_use_pathway",
        "status_notes",
    ],
    "energy.csv": [
        "energy_id",
        "plant_id",
        "electricity_demand_gwh",
        "heat_demand_gwh",
        "primary_energy_source",
        "grid_region",
        "source_id",
    ],
    "logistics.csv": [
        "logistics_id",
        "plant_id",
        "nearest_port",
        "port_distance_km",
        "rail_access",
        "storage_hub_candidate",
        "transport_notes",
    ],
    "references.csv": ["source_id", "title", "publisher", "url", "accessed_date", "notes"],
    "data_quality.csv": ["quality_id", "plant_id", "field_group", "rating", "rationale", "reviewed_date"],
}

ID_FIELDS = {
    "plants.csv": "plant_id",
    "locations.csv": "location_id",
    "emissions.csv": "emission_id",
    "products.csv": "product_id",
    "point_sources.csv": "point_source_id",
    "capture_status.csv": "capture_status_id",
    "energy.csv": "energy_id",
    "logistics.csv": "logistics_id",
    "references.csv": "source_id",
    "data_quality.csv": "quality_id",
}

PLANT_TABLES = [
    "locations.csv",
    "emissions.csv",
    "products.csv",
    "point_sources.csv",
    "capture_status.csv",
    "energy.csv",
    "logistics.csv",
    "data_quality.csv",
]
REFERENCE_TABLES = ["emissions.csv", "products.csv", "energy.csv"]
STATUS_VALUES = {"operational", "planned", "construction", "paused", "retired"}
READINESS_VALUES = {"none", "screening", "pilot", "planned", "installed"}
QUALITY_VALUES = {"high", "medium", "low"}


def read_csv(file_name: str) -> list[dict[str, str]]:
    with (DATA_DIR / file_name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def require_float(errors: list[str], file_name: str, line: int, field: str, value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        errors.append(f"{file_name}:{line} {field} must be numeric")
        return None


def require_int(errors: list[str], file_name: str, line: int, field: str, value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        errors.append(f"{file_name}:{line} {field} must be an integer")
        return None


def validate() -> list[str]:
    errors: list[str] = []
    tables = {file_name: read_csv(file_name) for file_name in REQUIRED_COLUMNS}

    for file_name, rows in tables.items():
        expected = REQUIRED_COLUMNS[file_name]
        id_field = ID_FIELDS[file_name]
        seen_ids: set[str] = set()
        for line, row in enumerate(rows, start=2):
            if list(row.keys()) != expected:
                errors.append(f"{file_name}:{line} columns must be: {', '.join(expected)}")
            for field in expected:
                if row.get(field, "") == "":
                    errors.append(f"{file_name}:{line} {field} is required")
            row_id = row.get(id_field, "")
            if row_id in seen_ids:
                errors.append(f"{file_name}:{line} duplicate {id_field}: {row_id}")
            seen_ids.add(row_id)

    plant_ids = {row["plant_id"] for row in tables["plants.csv"]}
    source_ids = {row["source_id"] for row in tables["references.csv"]}

    for table in PLANT_TABLES:
        for line, row in enumerate(tables[table], start=2):
            if row["plant_id"] not in plant_ids:
                errors.append(f"{table}:{line} unknown plant_id: {row['plant_id']}")

    for table in REFERENCE_TABLES:
        for line, row in enumerate(tables[table], start=2):
            if row["source_id"] not in source_ids:
                errors.append(f"{table}:{line} unknown source_id: {row['source_id']}")

    for line, row in enumerate(tables["plants.csv"], start=2):
        if row["status"] not in STATUS_VALUES:
            errors.append(f"plants.csv:{line} status must be one of {sorted(STATUS_VALUES)}")
        start_year = require_int(errors, "plants.csv", line, "start_year", row["start_year"])
        if start_year and (start_year < 1800 or start_year > date.today().year + 20):
            errors.append(f"plants.csv:{line} start_year is outside accepted range")
        parsed_url = urlparse(row["website"])
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            errors.append(f"plants.csv:{line} website must be an absolute http(s) URL")

    for line, row in enumerate(tables["locations.csv"], start=2):
        latitude = require_float(errors, "locations.csv", line, "latitude", row["latitude"])
        longitude = require_float(errors, "locations.csv", line, "longitude", row["longitude"])
        if latitude is not None and not -90 <= latitude <= 90:
            errors.append(f"locations.csv:{line} latitude out of range")
        if longitude is not None and not -180 <= longitude <= 180:
            errors.append(f"locations.csv:{line} longitude out of range")

    non_negative_fields = {
        "emissions.csv": ["co2e_tonnes"],
        "products.csv": ["annual_capacity_tonnes"],
        "point_sources.csv": ["estimated_co2_concentration_pct", "annual_co2_tonnes"],
        "capture_status.csv": ["target_capture_tonnes_per_year"],
        "energy.csv": ["electricity_demand_gwh", "heat_demand_gwh"],
        "logistics.csv": ["port_distance_km"],
    }
    for file_name, fields in non_negative_fields.items():
        for line, row in enumerate(tables[file_name], start=2):
            for field in fields:
                value = require_float(errors, file_name, line, field, row[field])
                if value is not None and value < 0:
                    errors.append(f"{file_name}:{line} {field} must be non-negative")

    for line, row in enumerate(tables["point_sources.csv"], start=2):
        pct = require_float(
            errors,
            "point_sources.csv",
            line,
            "estimated_co2_concentration_pct",
            row["estimated_co2_concentration_pct"],
        )
        if pct is not None and pct > 100:
            errors.append("point_sources.csv:{line} estimated_co2_concentration_pct must be <= 100")

    for line, row in enumerate(tables["capture_status.csv"], start=2):
        if row["readiness"] not in READINESS_VALUES:
            errors.append(f"capture_status.csv:{line} readiness must be one of {sorted(READINESS_VALUES)}")

    for line, row in enumerate(tables["data_quality.csv"], start=2):
        if row["rating"] not in QUALITY_VALUES:
            errors.append(f"data_quality.csv:{line} rating must be one of {sorted(QUALITY_VALUES)}")

    for line, row in enumerate(tables["references.csv"], start=2):
        parsed_url = urlparse(row["url"])
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            errors.append(f"references.csv:{line} url must be an absolute http(s) URL")
        try:
            date.fromisoformat(row["accessed_date"])
        except ValueError:
            errors.append(f"references.csv:{line} accessed_date must be ISO date")

    geojson_path = DATA_DIR / "locations.geojson"
    if geojson_path.exists():
        with geojson_path.open(encoding="utf-8") as handle:
            geojson = json.load(handle)
        geojson_plant_ids = {feature["properties"]["plant_id"] for feature in geojson.get("features", [])}
        location_plant_ids = {row["plant_id"] for row in tables["locations.csv"]}
        if geojson_plant_ids != location_plant_ids:
            errors.append("locations.geojson plant IDs must match locations.csv")
    else:
        errors.append("locations.geojson is missing")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Data validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Data validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

