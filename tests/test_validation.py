from scripts.validate_data import validate


def test_norway_data_validates() -> None:
    assert validate() == []

