"""SmartDeviceView tests — frozen snapshot, ID/name lookups, state accessors."""

import pytest

from sc_smart_device import SmartDeviceView

from sc_fixtures import (
    DEVICE_CLIENTNAME,
    DEVICE_ID,
    INPUT_1_NAME,
    INPUT_2_NAME,
    METER_1_NAME,
    METER_2_NAME,
    OUTPUT_1_NAME,
    OUTPUT_2_NAME,
    smart_device,
)


def test_get_view_returns_smart_device_view():
    """get_view() should return a SmartDeviceView instance."""
    view = smart_device.get_view()
    assert view is not None, "get_view() should not return None"
    assert isinstance(view, SmartDeviceView), "get_view() should return a SmartDeviceView"


def test_view_device_id_list():
    """View should list all configured device IDs (Shelly + Tasmota)."""
    view = smart_device.get_view()
    id_list = view.get_device_id_list()
    assert isinstance(id_list, list), "get_device_id_list() should return a list"
    assert len(id_list) == 2, "Should have exactly two devices (one Shelly, one Tasmota)"
    assert DEVICE_ID in id_list, f"Device ID {DEVICE_ID} should be in the list"


def test_view_validate_device_id():
    """validate_device_id() should accept valid IDs and names, reject unknown ones."""
    view = smart_device.get_view()
    assert view.validate_device_id(DEVICE_ID), "Valid device ID should pass validation"
    assert view.validate_device_id(DEVICE_CLIENTNAME), "Valid device name should pass validation"
    assert not view.validate_device_id(999), "Unknown device ID should fail validation"
    assert not view.validate_device_id("No Such Device"), "Unknown device name should fail validation"


def test_view_get_device_id():
    """get_device_id() should resolve device name to its ID."""
    view = smart_device.get_view()
    device_id = view.get_device_id(DEVICE_CLIENTNAME)
    assert device_id == DEVICE_ID, f"Device name '{DEVICE_CLIENTNAME}' should resolve to ID {DEVICE_ID}"
    assert view.get_device_id("No Such Device") == 0, "Unknown device name should return 0"


def test_view_get_device_name():
    """get_device_name() should resolve device ID to its name."""
    view = smart_device.get_view()
    name = view.get_device_name(DEVICE_ID)
    assert name == DEVICE_CLIENTNAME, f"Device ID {DEVICE_ID} should resolve to '{DEVICE_CLIENTNAME}'"


def test_view_get_device_name_invalid():
    """get_device_name() should raise IndexError for an unknown ID."""
    view = smart_device.get_view()
    with pytest.raises(IndexError):
        view.get_device_name(999)


def test_view_device_online():
    """get_device_online() should return True; all_devices_online() should agree."""
    view = smart_device.get_view()
    online = view.get_device_online(DEVICE_ID)
    assert isinstance(online, bool), "get_device_online() should return a bool"
    assert online is True, "Simulated device should always report online"
    assert view.all_devices_online(), "all_devices_online() should be True when all devices are online"


def test_view_device_expect_offline():
    """get_device_expect_offline() should return False for our test device."""
    view = smart_device.get_view()
    expect_offline = view.get_device_expect_offline(DEVICE_ID)
    assert isinstance(expect_offline, bool), "get_device_expect_offline() should return a bool"
    assert expect_offline is False, "Test device is not configured as ExpectOffline"


def test_view_get_json_snapshot():
    """get_json_snapshot() should return a dict with the right component counts.

    Test config: 1 Shelly (2 inputs, 2 outputs, 2 meters) + 1 Tasmota (0 inputs, 1 output, 1 meter).
    """
    view = smart_device.get_view()
    snapshot = view.get_json_snapshot()
    assert isinstance(snapshot, dict), "get_json_snapshot() should return a dict"
    for key in ("devices", "outputs", "inputs", "meters", "temp_probes"):
        assert key in snapshot, f"Snapshot should contain '{key}'"
    assert len(snapshot["devices"]) == 2, "Snapshot should contain 2 devices"
    assert len(snapshot["inputs"]) == 2, "Snapshot should contain 2 inputs (Shelly only)"
    assert len(snapshot["outputs"]) == 3, "Snapshot should contain 3 outputs (2 Shelly + 1 Tasmota)"
    assert len(snapshot["meters"]) == 3, "Snapshot should contain 3 meters (2 Shelly + 1 Tasmota)"


def test_view_output_id_lookup():
    """get_output_id() should resolve output names to IDs; unknown names return 0."""
    view = smart_device.get_view()
    output_id = view.get_output_id(OUTPUT_1_NAME)
    assert isinstance(output_id, int), "get_output_id() should return an int"
    assert output_id != 0, f"Output '{OUTPUT_1_NAME}' should have a non-zero ID"
    assert view.get_output_id("No Such Output") == 0, "Unknown output name should return 0"


def test_view_validate_output_id():
    """validate_output_id() should accept valid IDs and names, reject unknown ones."""
    view = smart_device.get_view()
    output_id = view.get_output_id(OUTPUT_1_NAME)
    assert view.validate_output_id(output_id), "Valid output ID should pass validation"
    assert view.validate_output_id(OUTPUT_1_NAME), "Valid output name should pass validation"
    assert not view.validate_output_id(999), "Unknown output ID should fail validation"
    assert not view.validate_output_id("No Such Output"), "Unknown output name should fail validation"


def test_view_output_state():
    """get_output_state() should return a bool for all Shelly outputs."""
    view = smart_device.get_view()
    for name in (OUTPUT_1_NAME, OUTPUT_2_NAME):
        output_id = view.get_output_id(name)
        state = view.get_output_state(output_id)
        assert isinstance(state, bool), f"Output state for '{name}' should be a bool"


def test_view_get_output_value():
    """get_output_value() should return the output Name field."""
    view = smart_device.get_view()
    for name in (OUTPUT_1_NAME, OUTPUT_2_NAME):
        output_id = view.get_output_id(name)
        value = view.get_output_value(output_id, key_name="Name")
        assert value is not None, "Output should have a Name value"


def test_view_output_state_invalid():
    """get_output_state() should raise IndexError for an unknown output ID."""
    view = smart_device.get_view()
    with pytest.raises(IndexError):
        view.get_output_state(999)


def test_view_output_device_id():
    """get_output_device_id() should link each Shelly output back to its parent device."""
    view = smart_device.get_view()
    for name in (OUTPUT_1_NAME, OUTPUT_2_NAME):
        output_id = view.get_output_id(name)
        parent_id = view.get_output_device_id(output_id)
        assert parent_id == DEVICE_ID, f"Output '{name}' should belong to device ID {DEVICE_ID}"


def test_view_input_id_lookup():
    """get_input_id() should resolve input names to IDs."""
    view = smart_device.get_view()
    for name in (INPUT_1_NAME, INPUT_2_NAME):
        input_id = view.get_input_id(name)
        assert isinstance(input_id, int), "get_input_id() should return an int"
        assert input_id != 0, f"Input '{name}' should have a non-zero ID"
    assert view.get_input_id("No Such Input") == 0, "Unknown input name should return 0"


def test_view_input_state():
    """get_input_state() should return a bool for all Shelly inputs."""
    view = smart_device.get_view()
    for name in (INPUT_1_NAME, INPUT_2_NAME):
        input_id = view.get_input_id(name)
        state = view.get_input_state(input_id)
        assert isinstance(state, bool), f"Input state for '{name}' should be a bool"


def test_view_input_state_invalid():
    """get_input_state() should raise IndexError for an unknown input ID."""
    view = smart_device.get_view()
    with pytest.raises(IndexError):
        view.get_input_state(999)


def test_view_meter_id_lookup():
    """get_meter_id() should resolve meter names to IDs."""
    view = smart_device.get_view()
    for name in (METER_1_NAME, METER_2_NAME):
        meter_id = view.get_meter_id(name)
        assert isinstance(meter_id, int), "get_meter_id() should return an int"
        assert meter_id != 0, f"Meter '{name}' should have a non-zero ID"
    assert view.get_meter_id("No Such Meter") == 0, "Unknown meter name should return 0"


def test_view_meter_energy():
    """get_meter_energy() should return a non-negative float."""
    view = smart_device.get_view()
    for name in (METER_1_NAME, METER_2_NAME):
        meter_id = view.get_meter_id(name)
        energy = view.get_meter_energy(meter_id)
        assert isinstance(energy, float), f"Meter energy for '{name}' should be a float"
        assert energy >= 0.0, f"Meter energy for '{name}' should be non-negative"


def test_view_meter_power():
    """get_meter_power() should return a non-negative float."""
    view = smart_device.get_view()
    for name in (METER_1_NAME, METER_2_NAME):
        meter_id = view.get_meter_id(name)
        power = view.get_meter_power(meter_id)
        assert isinstance(power, float), f"Meter power for '{name}' should be a float"
        assert power >= 0.0, f"Meter power for '{name}' should be non-negative"


def test_view_meter_invalid():
    """get_meter_energy/power should raise IndexError for an unknown meter ID."""
    view = smart_device.get_view()
    with pytest.raises(IndexError):
        view.get_meter_energy(999)
    with pytest.raises(IndexError):
        view.get_meter_power(999)


def test_view_is_frozen_snapshot():
    """A view snapshot should NOT reflect state changes made after it was taken.

    After changing an output, the old view should still show the old state.
    A freshly created view should show the new state.
    """
    output_name = OUTPUT_2_NAME
    output_id = smart_device.get_view().get_output_id(output_name)

    # Capture state before the change
    view_before = smart_device.get_view()
    state_before = view_before.get_output_state(output_id)

    # Change the output via the mutable control interface
    smart_device.change_output(output_name, not state_before)

    # The old view must still report the old state (it's frozen)
    assert view_before.get_output_state(output_id) == state_before, (
        "Existing view should be frozen and not reflect state changes"
    )

    # A new view taken after the change should reflect the new state
    view_after = smart_device.get_view()
    assert view_after.get_output_state(output_id) != state_before, (
        "New view should reflect the updated output state"
    )

    # Restore original state
    smart_device.change_output(output_name, state_before)
