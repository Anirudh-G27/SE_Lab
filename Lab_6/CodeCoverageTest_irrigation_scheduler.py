
import pytest
from irrigation_scheduler import should_irrigate, water_volume, schedule


# Tests for should_irrigate()

def test_wet_soil():
    assert should_irrigate(70, 0, "seedling") is False


def test_heavy_rain():
    assert should_irrigate(40, 10, "seedling") is False


def test_seedling_needs_water():
    assert should_irrigate(40, 0, "seedling") is True


def test_seedling_does_not_need_water():
    assert should_irrigate(50, 0, "seedling") is False


def test_flowering_needs_water():
    assert should_irrigate(40, 0, "flowering") is True


def test_flowering_does_not_need_water():
    assert should_irrigate(55, 0, "flowering") is False


def test_other_stage_rain():
    assert should_irrigate(30, 5, "vegetative") is False


def test_other_stage_needs_water():
    assert should_irrigate(30, 0, "vegetative") is True


# Tests for water_volume()

def test_invalid_zero_area():
    with pytest.raises(ValueError, match="invalid area"):
        water_volume(0, "seedling", 20)


def test_invalid_negative_area():
    with pytest.raises(ValueError, match="invalid area"):
        water_volume(-5, "seedling", 20)


def test_seedling_volume():
    assert water_volume(10, "seedling", 20) == 20


def test_flowering_volume():
    assert water_volume(10, "flowering", 20) == 50


def test_other_stage_volume():
    assert water_volume(10, "vegetative", 20) == 40


def test_high_temperature():
    assert water_volume(10, "seedling", 36) == 30


def test_low_temperature():
    assert water_volume(10, "seedling", 9) == 10


# Tests for schedule()

def test_empty_schedule():
    assert schedule([], 100) == []


def test_schedule_skips_wet_zone():
    zones = [("A", 10, 70, 0, "seedling", 20)]
    assert schedule(zones, 100) == []


def test_schedule_adds_zone():
    zones = [("A", 10, 40, 0, "seedling", 20)]
    assert schedule(zones, 20) == ["A"]


def test_schedule_stops_when_budget_insufficient():
    zones = [("A", 10, 40, 0, "seedling", 20)]
    assert schedule(zones, 10) == []


def test_schedule_multiple_zones():
    zones = [
        ("Wet", 10, 70, 0, "seedling", 20),
        ("Dry", 10, 40, 0, "seedling", 20),
        ("Flowers", 4, 40, 0, "flowering", 20)
    ]
    assert schedule(zones, 40) == ["Dry", "Flowers"]
