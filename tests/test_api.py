from fastapi import HTTPException

from api.carbon_api import health, locations_geojson, plant_detail, plants


def test_health() -> None:
    assert health() == {"status": "ok"}


def test_plants() -> None:
    assert len(plants(county=None, sector=None, status=None)) == 6
    assert len(plants(county="Vestland", sector=None, status=None)) == 2


def test_plant_detail() -> None:
    body = plant_detail("plant-brevik")
    assert body["plant"]["name"] == "Heidelberg Materials Brevik"
    assert body["location"]["county"] == "Telemark"


def test_geojson() -> None:
    body = locations_geojson(county=None, sector=None)
    assert body["type"] == "FeatureCollection"
    assert len(body["features"]) == 6


def test_plant_not_found() -> None:
    try:
        plant_detail("missing")
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("Expected HTTPException")
