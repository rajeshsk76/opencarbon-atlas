# Schema

All v1 data lives in `data/norway`.

Every CSV data row must include the v1 governance fields:

- `reference_id` pointing to `references.csv`.
- `data_quality` using the A-E evidence scale.
- `method` describing how the value was obtained.

The A-E data-quality scale is:

- `A` = government reported
- `B` = company annual report or official company page
- `C` = scientific paper
- `D` = engineering calculation
- `E` = assumption / unverified

## plants.csv

Facility identity and classification. Primary key: `plant_id`.

## locations.csv

One representative location per plant. Foreign key: `plant_id`.

## emissions.csv

Annual facility emissions by scope. Foreign keys: `plant_id`, `reference_id`.

## products.csv

Primary product and capacity estimates. Foreign keys: `plant_id`, `reference_id`.

## point_sources.csv

Major source streams that could be evaluated for capture.

## capture_status.csv

Capture readiness and pathway assumptions. `readiness` must be one of `none`, `screening`, `pilot`, `planned`, or `installed`.

## energy.csv

Screening-level electricity and heat demand context. Foreign keys: `plant_id`, `reference_id`.

## logistics.csv

Port, rail, storage-hub, and transport context.

## references.csv

Reference registry. Primary key: `reference_id`.

## data_quality.csv

Review notes by plant and field group. `data_quality` must be one of `A`, `B`, `C`, `D`, or `E`.

## locations.geojson

Derived from `plants.csv` and `locations.csv` by `scripts/build_geojson.py`.
