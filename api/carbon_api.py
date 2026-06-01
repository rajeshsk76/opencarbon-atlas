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
app.mount(
    "/dashboard",
    StaticFiles(directory=ROOT_DIR / "web" / "dashboard", html=True),
    name="dashboard",
)


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


def latest_total_scope1_emissions() -> dict[str, dict[str, object]]:
    latest_emissions: dict[str, dict[str, object]] = {}
    for row in load_tables()["emissions"]:
        if row["emission_type"] != "total_scope1_co2e":
            continue
        plant_id = str(row["plant_id"])
        current = latest_emissions.get(plant_id)
        if current is None or int(row["year"]) > int(current["year"]):
            latest_emissions[plant_id] = row
    return latest_emissions


@app.get("/geojson")
def dashboard_geojson() -> dict[str, object]:
    tables = load_tables()
    geojson = load_geojson()
    latest_emissions = latest_total_scope1_emissions()
    capture_by_plant = {str(row["plant_id"]): row for row in tables["capture_status"]}

    features = []
    for feature in geojson["features"]:
        properties = dict(feature["properties"])
        plant_id = str(properties["plant_id"])
        emission = latest_emissions.get(plant_id, {})
        capture = capture_by_plant.get(plant_id, {})
        properties.update(
            {
                "emissions": emission.get("value"),
                "emissions_unit": emission.get("unit"),
                "emissions_year": emission.get("year"),
                "capture_status": capture.get("capture_status", "none"),
                "reference_id": emission.get("reference_id"),
                "data_quality": emission.get("data_quality"),
            }
        )
        features.append({**feature, "properties": properties})

    return {"type": "FeatureCollection", "features": features}


@app.get("/analytics/sector-emissions")
def sector_emissions() -> list[dict[str, object]]:
    tables = load_tables()
    plants_by_id = {str(row["plant_id"]): row for row in tables["plants"]}
    totals: dict[str, float] = {}
    for row in latest_total_scope1_emissions().values():
        plant = plants_by_id[str(row["plant_id"])]
        sector_name = str(plant["sector"])
        totals[sector_name] = totals.get(sector_name, 0.0) + float(row["value"])
    return [
        {"sector": sector_name, "total_scope1_co2e": total}
        for sector_name, total in sorted(totals.items())
    ]


@app.get("/analytics/capture-status")
def capture_status_analytics() -> list[dict[str, object]]:
    counts: dict[str, int] = {}
    for row in load_tables()["capture_status"]:
        status = str(row["capture_status"])
        counts[status] = counts.get(status, 0) + 1
    return [{"capture_status": status, "count": count} for status, count in sorted(counts.items())]


@app.get("/analytics/data-quality")
def data_quality_analytics() -> list[dict[str, object]]:
    counts = {grade: 0 for grade in ["A", "B", "C", "D", "E"]}
    governed_tables = [
        "plants",
        "locations",
        "emissions",
        "products",
        "point_sources",
        "capture_status",
        "energy",
        "logistics",
    ]
    tables = load_tables()
    for table in governed_tables:
        for row in tables[table]:
            grade = row.get("data_quality")
            if grade in counts:
                counts[str(grade)] += 1
    return [{"data_quality": grade, "count": count} for grade, count in counts.items()]


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
        "latest_emissions_tonnes": sum(float(row["value"]) for row in latest_emissions.values()),
        "point_source_count": len(tables["point_sources"]),
        "by_sector": by_sector,
    }
