"""pytest for SCSmartDevice class."""
import sys

import pytest
from sc_foundation import SCConfigManager, SCLogger

from sc_smart_device import SCSmartDevice, SmartDeviceView, smart_devices_validator

CONFIG_FILE = "tests/config.yaml"
DEVICE_CLIENTNAME = "Device Test 1"

print("Running test for SCSmartDevice...")

# Initialize the SC_ConfigManager class
try:
    config = SCConfigManager(
        config_file=CONFIG_FILE,
        validation_schema=smart_devices_validator,
    )
except RuntimeError as e:
    print(f"Configuration file error: {e}", file=sys.stderr)
    sys.exit(1)
else:
    assert config is not None, "ConfigManager should be initialized"


# Initialize the SC_Logger class
try:
    logger = SCLogger(config.get_logger_settings())
except RuntimeError as e:
    print(f"Logger initialisation error: {e}", file=sys.stderr)
    sys.exit(1)
else:
    assert logger is not None, "Logger should be initialized"

# Create the SCSmartDevice object
smart_switch_settings = config.get("SCSmartDevices")
assert smart_switch_settings is not None, "SCSmartDevice settings should be initialized"

# Initialize the SC_SCSmartDevice class
try:
    smart_device = SCSmartDevice(logger, smart_switch_settings)  # type: ignore[call-arg]
except RuntimeError as e:
    print(f"Shelly control initialization error: {e}", file=sys.stderr)
    sys.exit(1)
else:
    assert smart_device is not None, "SCSmartDevice should be initialized"


def test_get_device():
    """Test function for SCSmartDevice."""
    assert smart_device is not None, "SCSmartDevice should be initialized"
    try:
        device = smart_device.get_device(DEVICE_CLIENTNAME)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    else:
        assert device is not None, f"Device {DEVICE_CLIENTNAME} should be found"
        assert isinstance(device, dict), "Device should be a dictionary"
        assert device.get("Index") == 0, "Device Index should be 0"
        assert device.get("ClientName") == DEVICE_CLIENTNAME, f"Device identity should be {DEVICE_CLIENTNAME}"
        assert device.get("Model") == "Shelly2PMG3", "Device Model should be Shelly2PMG3"
        assert device.get("Inputs") == 2, "Device input count should be 2"
        assert device.get("Outputs") == 2, "Device output count should be 2"
        assert device.get("Meters") == 2, "Device meter  count should be 2"


def test_get_device_information():
    """Test function for SCSmartDevice."""
    assert smart_device is not None, "SCSmartDevice should be initialized"
    try:
        device = smart_device.get_device(DEVICE_CLIENTNAME)
        device_info = smart_device.get_device_information(device)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    else:
        assert device_info is not None, f"Device {DEVICE_CLIENTNAME} information should be found"
        assert isinstance(device_info, dict), f"Device {DEVICE_CLIENTNAME} information should be a dict"
        assert device_info.get("Model") == "Shelly2PMG3", "Device information should contain model information"
        assert len(device_info.get("Inputs")) == 2, "Device information should contain 2 inputs"  # type: ignore[call-arg]
        assert len(device_info.get("Outputs")) == 2, "Device information should contain 2 outputs"  # type: ignore[call-arg]
        assert len(device_info.get("Meters")) == 2, "Device information should contain 2 meters"  # type: ignore[call-arg]


def test_get_device_status():
    """Test function for SCSmartDevice."""
    assert smart_device is not None, "SCSmartDevice should be initialized"
    try:
        device = smart_device.get_device(DEVICE_CLIENTNAME)
        result = smart_device.get_device_status(device)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    else:
        assert result is not None, f"Device {DEVICE_CLIENTNAME} status should be found"

    device_input = smart_device.get_device_component("input", "Device 1.Input 1")
    assert device_input is not None, "Device input should be found"
    assert device_input.get("State") is not None, "Device input state should be found"
    assert isinstance(device_input.get("State"), bool), "Device input state should be a boolean"

    device_output = smart_device.get_device_component("output", "Device 1.Output 2")
    assert device_output is not None, "Device output should be found"
    assert device_output.get("State") is not None, "Device output state should be found"
    assert isinstance(device_output.get("State"), bool), "Device output state should be a boolean"

    device_meter = smart_device.get_device_component("meter", "Meter 1")  # Auto generated name
    assert device_meter is not None, "Device meter should be found"


def test_refresh_all_device_statuses():
    """Test function for refreshing all device statuses."""
    assert smart_device is not None, "SCSmartDevice should be initialized"
    try:
        smart_device.refresh_all_device_statuses()
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def test_is_device_online():
    """Test function for checking if a device is online."""
    assert smart_device is not None, "SCSmartDevice should be initialized"
    try:
        is_online = smart_device.is_device_online(DEVICE_CLIENTNAME)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    else:
        assert is_online, f"Device {DEVICE_CLIENTNAME} should be online"


def test_print_device_status():
    """Test function for printing device status."""
    assert smart_device is not None, "SCSmartDevice should be initialized"
    try:
        device_status = smart_device.print_device_status(DEVICE_CLIENTNAME)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    else:
        assert device_status is not None, f"Device {DEVICE_CLIENTNAME} status should be printed"
        assert isinstance(device_status, str), f"Device {DEVICE_CLIENTNAME} status should be a string"
        assert device_status.find("Generation: ") != -1, "Device status should contain generation information"


def test_print_model_library():
    """Test function for printing model library."""
    assert smart_device is not None, "SCSmartDevice should be initialized"
    try:
        model_library = smart_device.print_model_library(mode_str="brief")
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    else:
        assert model_library is not None, "Model library should be printed"
        assert isinstance(model_library, str), "Model library should be a string"
        assert model_library.find("Shelly2PMG3") != -1, "Model library should contain Shelly2PMG3 model"


def test_change_output():
    """Test function for changing output state."""
    assert smart_device is not None, "SCSmartDevice should be initialized"
    try:
        output_identity = "Device 1.Output 1"  # Example output identity
        output_obj = smart_device.get_device_component("output", output_identity)
        current_state = output_obj["State"]
        result, did_change = smart_device.change_output(output_identity, not current_state)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    else:
        assert result, f"Output {output_identity} state changed successfully"
        assert did_change, f"Output {output_identity} state should have changed"
        # Optionally, you can check the new state of the output
        new_state = smart_device.get_device_component("output", output_identity)["State"]
        assert new_state != current_state, "Output state should be changed"


# ── SmartDeviceView tests ────────────────────────────────────────────────────

DEVICE_ID = 1           # Auto-assigned (first device, no explicit ID in config)
OUTPUT_1_NAME = "Device 1.Output 1"
OUTPUT_2_NAME = "Device 1.Output 2"
INPUT_1_NAME = "Device 1.Input 1"
INPUT_2_NAME = "Device 1.Input 2"
METER_1_NAME = "Meter 1"   # Auto-generated (no Meters: block in config)
METER_2_NAME = "Meter 2"


def test_get_view_returns_smart_device_view():
    """get_view() should return a SmartDeviceView instance."""
    view = smart_device.get_view()
    assert view is not None, "get_view() should not return None"
    assert isinstance(view, SmartDeviceView), "get_view() should return a SmartDeviceView"


def test_view_device_id_list():
    """View should list all configured device IDs."""
    view = smart_device.get_view()
    id_list = view.get_device_id_list()
    assert isinstance(id_list, list), "get_device_id_list() should return a list"
    assert len(id_list) == 1, "Should have exactly one device"
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
    """get_device_online() should return a bool; all_devices_online() should agree."""
    view = smart_device.get_view()
    online = view.get_device_online(DEVICE_ID)
    assert isinstance(online, bool), "get_device_online() should return a bool"
    # Simulation mode forces Online=True
    assert online is True, "Simulated device should always report online"
    assert view.all_devices_online(), "all_devices_online() should be True when all devices are online"


def test_view_device_expect_offline():
    """get_device_expect_offline() should return False for our test device."""
    view = smart_device.get_view()
    expect_offline = view.get_device_expect_offline(DEVICE_ID)
    assert isinstance(expect_offline, bool), "get_device_expect_offline() should return a bool"
    assert expect_offline is False, "Test device is not configured as ExpectOffline"


def test_view_get_json_snapshot():
    """get_json_snapshot() should return a dict with all component lists."""
    view = smart_device.get_view()
    snapshot = view.get_json_snapshot()
    assert isinstance(snapshot, dict), "get_json_snapshot() should return a dict"
    for key in ("devices", "outputs", "inputs", "meters", "temp_probes"):
        assert key in snapshot, f"Snapshot should contain '{key}'"
    assert len(snapshot["devices"]) == 1, "Snapshot should contain one device"
    assert len(snapshot["inputs"]) == 2, "Snapshot should contain 2 inputs"
    assert len(snapshot["outputs"]) == 2, "Snapshot should contain 2 outputs"
    assert len(snapshot["meters"]) == 2, "Snapshot should contain 2 meters"


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
    """get_output_state() should return a bool for both outputs."""
    view = smart_device.get_view()
    for name in (OUTPUT_1_NAME, OUTPUT_2_NAME):
        output_id = view.get_output_id(name)
        state = view.get_output_state(output_id)
        assert isinstance(state, bool), f"Output state for '{name}' should be a bool"


def test_view_output_state_invalid():
    """get_output_state() should raise IndexError for an unknown output ID."""
    view = smart_device.get_view()
    with pytest.raises(IndexError):
        view.get_output_state(999)


def test_view_output_device_id():
    """get_output_device_id() should link each output back to its parent device."""
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
    """get_input_state() should return a bool for both inputs."""
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
    """get_meter_energy() should return a float (0.0 when no readings yet)."""
    view = smart_device.get_view()
    for name in (METER_1_NAME, METER_2_NAME):
        meter_id = view.get_meter_id(name)
        energy = view.get_meter_energy(meter_id)
        assert isinstance(energy, float), f"Meter energy for '{name}' should be a float"
        assert energy >= 0.0, f"Meter energy for '{name}' should be non-negative"


def test_view_meter_power():
    """get_meter_power() should return a float (0.0 when no readings yet)."""
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
