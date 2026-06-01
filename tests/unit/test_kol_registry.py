from src.scoring.kol_registry import find_kol_weight, load_kol_registry


def test_load_kol_registry_contains_entries() -> None:
    registry = load_kol_registry()
    assert isinstance(registry, list)
    assert len(registry) >= 1


def test_find_kol_weight_by_handle() -> None:
    weight = find_kol_weight("@swyx")
    assert weight == 0.8
