import pytest
from irrigation_scheduler import should_irrigate, water_volume, schedule

#Example test cases:
def test_wet_soil_no_irrigation():
    assert should_irrigate(70, 0, "seedling") is False

def test_seedling_volume():
    assert water_volume(10, "seedling", 20) == 20

#Write the rest of the test cases so that the code is 90- 100% covered.
