from fastapi import HTTPException

from api.carbon_api import (
    capture_status_analytics,
    dashboard_geojson,
    data_quality_analytics,
    health,
    locations_geojson,
    plant_detail,
    plants,
    sector_emissions,
)


def test_health() -> None:
    assert health() == {"status": "ok"}


def test_plants() -> None:
    assert len(plants(county=None, sector=None, status=None)) == 5
    assert len(plants(county="Telemark", sector=None, status=None)) == 2


def test_plant_detail() -> None:
    body = plant_detail("NO-0002")
    assert body["plant"]["name"] == "Heidelberg Materials Brevik"
    assert body["location"]["county"] == "Telemark"
    assert body["emissions"][0]["emission_type"] == "total_scope1_co2e"
    assert body["emissions"][0]["reference_id"] == "REF-0001"


def test_geojson() -> None:
    body = locations_geojson(county=None, sector=None)
    assert body["type"] == "FeatureCollection"
    assert len(body["features"]) == 5


def test_dashboard_geojson() -> None:
    body = dashboard_geojson()
    first = body["features"][0]["properties"]
    assert body["type"] == "FeatureCollection"
    assert len(body["features"]) == 5
    assert first["emissions"] == 850000.0
    assert first["capture_status"] == "study"
    assert first["reference_id"] == "REF-0001"
    assert first["data_quality"] == "A"


def test_sector_emissions_analytics() -> None:
    body = sector_emissions()
    by_sector = {row["sector"]: row["total_scope1_co2e"] for row in body}
    assert by_sector["fertilizer"] == 850000.0
    assert by_sector["cement"] == 800000.0


def test_capture_status_analytics() -> None:
    body = capture_status_analytics()
    by_status = {row["capture_status"]: row["count"] for row in body}
    assert by_status["study"] == 3
    assert by_status["planned"] == 1
    assert by_status["under-construction"] == 1


def test_data_quality_analytics() -> None:
    body = data_quality_analytics()
    by_quality = {row["data_quality"]: row["count"] for row in body}
    assert by_quality["A"] == 5
    assert by_quality["B"] > 0
    assert by_quality["D"] > 0


def test_plant_not_found() -> None:
    try:
        plant_detail("missing")
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("Expected HTTPException")
