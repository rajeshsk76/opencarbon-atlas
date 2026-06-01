# OpenCarbon Atlas

OpenCarbon Atlas v1 is a Norway-focused industrial carbon point-source atlas. The repository is CSV-first: source tables live in `data/norway`, validation is scriptable, the API reads directly from the CSVs, and the Leaflet viewer uses the generated GeoJSON.

## v1 Scope

- Norway CSV tables for plants, locations, emissions, products, point sources, capture status, energy, logistics, references, and data quality.
- FastAPI backend under `api/` exposing plants, plant detail, summary stats, and GeoJSON.
- Leaflet viewer under `web/map_viewer/` with county and sector filters.
- Scripts to seed/check sample data, validate CSV integrity, and rebuild `locations.geojson`.
- Documentation for methodology, data sources, schema, contribution workflow, and roadmap.

## Data Governance

OpenCarbon Atlas v1 keeps data governance in the CSV layer. Every CSV data row must include:

- `reference_id` identifying the entry in `references.csv` that supports the row.
- `data_quality` using the v1 A-E evidence scale.
- `method` describing whether the value is reported, transcribed, calculated, estimated, or assumed.

The v1 data-quality scale is:

- `A` = government reported
- `B` = company annual report or official company page
- `C` = scientific paper
- `D` = engineering calculation
- `E` = assumption / unverified

## Quick Start

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
python scripts/build_geojson.py
python scripts/validate_data.py
uvicorn api.carbon_api:app --reload
```

Open `http://127.0.0.1:8000` for the map viewer.

## Repository Layout

```text
api/                 FastAPI backend
data/norway/         Norway CSV source tables and locations.geojson
docs/                Methodology, sources, schema, contribution, roadmap
scripts/             Validation, GeoJSON build, and seed checks
web/map_viewer/      Leaflet browser client
tests/               API and validation tests
```

## Data License

The seed dataset is illustrative and should be treated as a starter dataset, not as verified investment, regulatory, or engineering advice. Add reference URLs, `reference_id`, `data_quality`, and `method` values when contributing new records.
