# Methodology

OpenCarbon Atlas v1 is a Norway-focused screening dataset for industrial carbon point sources. It is designed to help compare facilities, emissions scale, capture readiness, and transport context using transparent CSV files.

The initial dataset uses facility-level rows for well-known Norwegian industrial emitters. Locations are representative site coordinates. Emissions, capacity, energy, and logistics values are rounded screening values and should be replaced with traceable source-specific values as the dataset matures.

Derived files are reproducible:

```bash
python scripts/build_geojson.py
python scripts/validate_data.py
```

