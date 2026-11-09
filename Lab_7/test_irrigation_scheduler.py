from hypothesis import given, strategies as st
from irrigation_scheduler import parse_zone, moisture_average, water_needed


@given(st.text() | st.none())
def test_parse_zone_no_crash(s):
    try:
        parse_zone(s)
    except Exception as e:
        assert False, f"parse_zone crashed with: {e!r} for input {s!r}"


@given(st.text() | st.none())
def test_moisture_average_no_crash(s):
    try:
        moisture_average(s)
    except Exception as e:
        assert False, f"moisture_average crashed with: {e!r} for input {s!r}"


@given(st.text() | st.none())
def test_water_needed_no_crash(s):
    try:
        water_needed(s)
    except Exception as e:
        assert False, f"water_needed crashed with: {e!r} for input {s!r}"