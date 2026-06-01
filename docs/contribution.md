# Contribution

1. Edit the CSV files in `data/norway`.
2. Add references to `references.csv` before using a new `source_id`.
3. Regenerate GeoJSON with `python scripts/build_geojson.py`.
4. Validate the dataset with `python scripts/validate_data.py`.
5. Run `pytest` before committing.

Use stable lowercase IDs such as `plant-example`, `loc-example`, and `src-example`. If coordinates or quantitative values are estimated, document that in `data_quality.csv`.

