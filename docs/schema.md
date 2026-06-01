# Schema

All v1 data lives in `data/norway`.

## plants.csv

Facility identity and classification. Primary key: `plant_id`.

## locations.csv

One representative location per plant. Foreign key: `plant_id`.

## emissions.csv

Annual facility emissions by scope. Foreign keys: `plant_id`, `source_id`.

## products.csv

Primary product and capacity estimates. Foreign keys: `plant_id`, `source_id`.

## point_sources.csv

Major source streams that could be evaluated for capture.

## capture_status.csv

Capture readiness and pathway assumptions. `readiness` must be one of `none`, `screening`, `pilot`, `planned`, or `installed`.

## energy.csv

Screening-level electricity and heat demand context. Foreign keys: `plant_id`, `source_id`.

## logistics.csv

Port, rail, storage-hub, and transport context.

## references.csv

Source registry. Primary key: `source_id`.

## data_quality.csv

Review notes by plant and field group. `rating` must be `high`, `medium`, or `low`.

## locations.geojson

Derived from `plants.csv` and `locations.csv` by `scripts/build_geojson.py`.

