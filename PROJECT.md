# OpenCarbon Atlas v1 Brief

Build a complete repository for OpenCarbon Atlas without modifying anything outside `/opt/opencarbon-atlas`.

The v1 scope is a Norway-focused carbon atlas with:

- CSV source data and schemas for industrial plants, locations, emissions, products, point sources, capture status, energy, logistics, references, and data quality.
- A FastAPI backend under `api/` using `carbon_api.py`, `database.py`, and `schemas.py`.
- A Leaflet map viewer under `web/map_viewer/`.
- Validation, GeoJSON build, and sample-data seeding scripts under `scripts/`.
- Documentation under `docs/` covering methodology, data sources, schema, contribution process, and roadmap.
- Seed data and derived `locations.geojson` under `data/norway/`.
- A proper Git repository with the completed implementation committed.

Requested repository structure:

```text
api/
  carbon_api.py
  database.py
  schemas.py

web/map_viewer/
  index.html
  map.js
  style.css

data/norway/
  plants.csv
  locations.csv
  emissions.csv
  products.csv
  point_sources.csv
  capture_status.csv
  energy.csv
  logistics.csv
  references.csv
  data_quality.csv
  locations.geojson

scripts/
  validate_data.py
  build_geojson.py
  seed_sample_data.py

docs/
  methodology.md
  data_sources.md
  schema.md
  contribution.md
  roadmap.md
```

