# Methodology

OpenCarbon Atlas v1 is a Norway-focused screening dataset for industrial carbon point sources. It is designed to help compare facilities, emissions scale, capture readiness, and transport context using transparent CSV files.

The initial dataset uses facility-level rows for well-known Norwegian industrial emitters. Locations are representative site coordinates. Emissions, capacity, energy, and logistics values are rounded screening values and should be replaced with traceable source-specific values as the dataset matures.

## Data Governance

OpenCarbon Atlas v1 keeps the original CSV-first governance model: each row must be traceable to a reference, carry a data-quality grade, and state the method used to obtain the value. Every CSV data row must include:

- `reference_id`
- `data_quality`
- `method`

Use the v1 A-E evidence scale for `data_quality`:

- `A` = government reported
- `B` = company annual report or official company page
- `C` = scientific paper
- `D` = engineering calculation
- `E` = assumption / unverified

Use `method` to describe the row's basis, such as reported, transcribed, engineering calculation, estimate, or assumption. Do not leave estimated or assumed values without a `reference_id`, `data_quality`, and `method`.

Derived files are reproducible:

```bash
python scripts/build_geojson.py
python scripts/validate_data.py
```
