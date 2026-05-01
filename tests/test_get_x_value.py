"""get_X_value() tests — custom-key lookups on SmartDeviceView."""

import pytest

from sc_fixtures import (
    DEVICE_CLIENTNAME,
    DEVICE_ID,
    INPUT_1_NAME,
    METER_1_NAME,
    OUTPUT_1_NAME,
    smart_device,
)


def test_view_get_device_value_standard_key():
    """get_device_value() should return standard normalized fields by key name."""
    view = smart_device.get_view()
    assert view.get_device_value(DEVICE_ID, "Name") == DEVICE_CLIENTNAME
    assert view.get_device_value(DEVICE_ID, "Online") is True  # simulation mode


def test_view_get_device_value_missing_key():
    """get_device_value() should return the default when the key is absent."""
    view = smart_device.get_view()
    assert view.get_device_value(DEVICE_ID, "NoSuchKey") is None
    assert view.get_device_value(DEVICE_ID, "NoSuchKey", "fallback") == "fallback"
    assert view.get_device_value(DEVICE_ID, "NoSuchKey", 42) == 42


def test_view_get_device_value_invalid_id():
    """get_device_value() should raise IndexError for an unknown device ID."""
    view = smart_device.get_view()
    with pytest.raises(IndexError):
        view.get_device_value(999, "Name")


def test_view_get_output_value_standard_key():
    """get_output_value() should return standard normalized fields by key name."""
    view = smart_device.get_view()
    output_id = view.get_output_id(OUTPUT_1_NAME)
    assert view.get_output_value(output_id, "Name") == OUTPUT_1_NAME
    assert isinstance(view.get_output_value(output_id, "State"), bool)


def test_view_get_output_value_missing_key():
    """get_output_value() should return the default for absent keys (e.g. custom keys)."""
    view = smart_device.get_view()
    output_id = view.get_output_id(OUTPUT_1_NAME)
    assert view.get_output_value(output_id, "XXX") is None
    assert view.get_output_value(output_id, "XXX", "Ungrouped") == "Ungrouped"


def test_view_get_output_value_invalid_id():
    """get_output_value() should raise IndexError for an unknown output ID."""
    view = smart_device.get_view()
    with pytest.raises(IndexError):
        view.get_output_value(999, "State")


def test_view_get_input_value_standard_key():
    """get_input_value() should return standard normalized fields by key name."""
    view = smart_device.get_view()
    input_id = view.get_input_id(INPUT_1_NAME)
    assert view.get_input_value(input_id, "Name") == INPUT_1_NAME
    assert isinstance(view.get_input_value(input_id, "State"), bool)


def test_view_get_input_value_missing_key():
    """get_input_value() should return the default for absent keys."""
    view = smart_device.get_view()
    input_id = view.get_input_id(INPUT_1_NAME)
    assert view.get_input_value(input_id, "NoSuchKey") is None
    assert view.get_input_value(input_id, "NoSuchKey", False) is False


def test_view_get_input_value_invalid_id():
    """get_input_value() should raise IndexError for an unknown input ID."""
    view = smart_device.get_view()
    with pytest.raises(IndexError):
        view.get_input_value(999, "State")


def test_view_get_meter_value_standard_key():
    """get_meter_value() should return standard normalized fields by key name."""
    view = smart_device.get_view()
    meter_id = view.get_meter_id(METER_1_NAME)
    assert view.get_meter_value(meter_id, "Name") == METER_1_NAME
    voltage = view.get_meter_value(meter_id, "Voltage")
    assert voltage is None or isinstance(voltage, (int, float))
    current = view.get_meter_value(meter_id, "Current")
    assert current is None or isinstance(current, (int, float))


def test_view_get_meter_value_missing_key():
    """get_meter_value() should return the default for absent keys."""
    view = smart_device.get_view()
    meter_id = view.get_meter_id(METER_1_NAME)
    assert view.get_meter_value(meter_id, "NoSuchKey") is None
    assert view.get_meter_value(meter_id, "NoSuchKey", 0.0) == 0.0  # noqa: RUF069


def test_view_get_meter_value_invalid_id():
    """get_meter_value() should raise IndexError for an unknown meter ID."""
    view = smart_device.get_view()
    with pytest.raises(IndexError):
        view.get_meter_value(999, "Power")
