from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.database import ROOT_DIR, get_plant_detail, load_geojson, load_tables

app = FastAPI(
    title="OpenCarbon Atlas Norway API",
    version="1.0.0",
    description="CSV-backed API for Norway industrial carbon point-source atlas data.",
)

app.mount("/viewer", StaticFiles(directory=ROOT_DIR / "web" / "map_viewer"), name="viewer")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(ROOT_DIR / "web" / "map_viewer" / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/plants")
def plants(
    county: str | None = Query(default=None),
    sector: str | None = Query(default=None),
    status: str | None = Query(default=None),
) -> list[dict[str, object]]:
    rows = load_tables()["plants"]
    if county:
        rows = [row for row in rows if str(row["county"]).lower() == county.lower()]
    if sector:
        rows = [row for row in rows if str(row["sector"]).lower() == sector.lower()]
    if status:
        rows = [row for row in rows if str(row["status"]).lower() == status.lower()]
    return rows


@app.get("/api/plants/{plant_id}")
def plant_detail(plant_id: str) -> dict[str, object]:
    detail = get_plant_detail(plant_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    return detail


@app.get("/api/locations.geojson")
def locations_geojson(
    county: str | None = Query(default=None),
    sector: str | None = Query(default=None),
) -> dict[str, object]:
    geojson = load_geojson()
    features = geojson["features"]
    if county:
        features = [feature for feature in features if feature["properties"]["county"].lower() == county.lower()]
    if sector:
        features = [feature for feature in features if feature["properties"]["sector"].lower() == sector.lower()]
    return {"type": "FeatureCollection", "features": features}


@app.get("/api/stats")
def stats() -> dict[str, object]:
    tables = load_tables()
    latest_emissions: dict[str, dict[str, object]] = {}
    for row in tables["emissions"]:
        current = latest_emissions.get(str(row["plant_id"]))
        if current is None or int(row["year"]) > int(current["year"]):
            latest_emissions[str(row["plant_id"])] = row

    by_sector: dict[str, int] = {}
    for row in tables["plants"]:
        by_sector[str(row["sector"])] = by_sector.get(str(row["sector"]), 0) + 1

    return {
        "plant_count": len(tables["plants"]),
        "latest_emissions_tonnes": sum(float(row["co2e_tonnes"]) for row in latest_emissions.values()),
        "point_source_count": len(tables["point_sources"]),
        "by_sector": by_sector,
    }

