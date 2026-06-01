# Contribution

1. Edit the CSV files in `data/norway`.
2. Add references to `references.csv` before using a new `reference_id`.
3. Regenerate GeoJSON with `python scripts/build_geojson.py`.
4. Validate the dataset with `python scripts/validate_data.py`.
5. Run `pytest` before committing.

Use stable lowercase IDs such as `plant-example`, `loc-example`, and `ref-example`.

Every CSV data row must include:

- `reference_id`
- `data_quality`
- `method`

Use the v1 A-E data-quality scale:

- `A` = government reported
- `B` = company annual report or official company page
- `C` = scientific paper
- `D` = engineering calculation
- `E` = assumption / unverified

If coordinates or quantitative values are estimated, set `data_quality` to the appropriate A-E value, describe the basis in `method`, and document the rationale in `data_quality.csv`.
