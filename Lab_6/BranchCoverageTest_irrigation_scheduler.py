
import pytest
from irrigation_scheduler import should_irrigate, water_volume, schedule


# Branch tests for should_irrigate()

def test_moisture_at_60():
    assert should_irrigate(60, 0, "seedling") is False


def test_moisture_below_60():
    assert should_irrigate(59, 0, "seedling") is False


def test_rain_at_10():
    assert should_irrigate(40, 10, "seedling") is False


def test_rain_below_10():
    assert should_irrigate(40, 9, "seedling") is True


def test_seedling_moisture_below_45():
    assert should_irrigate(44, 0, "seedling") is True


def test_seedling_moisture_at_45():
    assert should_irrigate(45, 0, "seedling") is False


def test_flowering_moisture_below_55():
    assert should_irrigate(54, 0, "flowering") is True


def test_flowering_moisture_at_55():
    assert should_irrigate(55, 0, "flowering") is False


def test_other_stage_rain_at_5():
    assert should_irrigate(30, 5, "vegetative") is False


def test_other_stage_rain_below_5():
    assert should_irrigate(30, 4, "vegetative") is True


def test_other_stage_moisture_at_40():
    assert should_irrigate(40, 0, "vegetative") is False


# Branch tests for water_volume()

def test_area_zero_raises_error():
    with pytest.raises(ValueError):
        water_volume(0, "seedling", 20)


def test_positive_area_accepted():
    assert water_volume(1, "seedling", 20) == 2


def test_seedling_stage():
    assert water_volume(1, "seedling", 20) == 2


def test_flowering_stage():
    assert water_volume(1, "flowering", 20) == 5


def test_other_stage():
    assert water_volume(1, "vegetative", 20) == 4


def test_temperature_above_35():
    assert water_volume(1, "seedling", 36) == 3


def test_temperature_at_35():
    assert water_volume(1, "seedling", 35) == 2


def test_temperature_below_10():
    assert water_volume(1, "seedling", 9) == 1


def test_temperature_at_10():
    assert water_volume(1, "seedling", 10) == 2


# Branch tests for schedule()

def test_empty_zones():
    assert schedule([], 100) == []


def test_zone_skipped():
    zones = [("Wet", 1, 70, 0, "seedling", 20)]
    assert schedule(zones, 100) == []


def test_budget_sufficient():
    zones = [("Dry", 1, 40, 0, "seedling", 20)]
    assert schedule(zones, 2) == ["Dry"]


def test_budget_insufficient_breaks_loop():
    zones = [("Dry", 1, 40, 0, "seedling", 20)]
    assert schedule(zones, 1) == []


def test_remaining_budget_used_for_next_zone():
    zones = [
        ("A", 1, 40, 0, "seedling", 20),
        ("B", 1, 40, 0, "seedling", 20)
    ]
    assert schedule(zones, 4) == ["A", "B"]
