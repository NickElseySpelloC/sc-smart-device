"""pytest for SCSmartDevice class."""
import sys

import pytest
from mergedeep import merge
from sc_foundation import SCConfigManager, SCLogger

from examples.validation_extras import smart_switch_extra_validation
from sc_smart_device import SCSmartDevice, SmartDeviceView, smart_devices_validator

CONFIG_FILE = "tests/config.yaml"
DEVICE_CLIENTNAME = "Device Test 1"

print("Running test for SCSmartDevice...")

# Merge the SmartDevices validation schema with the default validation schema
merged_schema = merge({}, smart_devices_validator, smart_switch_extra_validation)
assert isinstance(merged_schema, dict), "Merged schema should be type dict"

# Initialize the SC_ConfigManager class
try:
    config = SCConfigManager(
        config_file=CONFIG_FILE,
        validation_schema=merged_schema,
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
    assert device_output.get("Group") is not None, "Device output group should be found"

    # Test Group attribute for Device 1.Output 1
    device_output_1 = smart_device.get_device_component("output", "Device 1.Output 1")
    assert device_output_1 is not None, "Device output 1 should be found"
    assert device_output_1.get("Group") is not None, "Device output 1 Group attribute should exist"
    assert isinstance(device_output_1.get("Group"), str), "Device output 1 Group should be a string"

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
    """get_json_snapshot() should return a dict with all component lists.

    With the test config: 1 Shelly device (2 inputs, 2 outputs, 2 meters)
    + 1 Tasmota device (0 inputs, 1 output, 1 meter) = 2 devices total.
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
    """get_output_state() should return a bool for both outputs."""
    view = smart_device.get_view()
    for name in (OUTPUT_1_NAME, OUTPUT_2_NAME):
        output_id = view.get_output_id(name)
        state = view.get_output_state(output_id)
        assert isinstance(state, bool), f"Output state for '{name}' should be a bool"


def test_view_get_device_value():
    """get_device_value() should resolve device ID to its value."""
    view = smart_device.get_view()
    for name in (OUTPUT_1_NAME, OUTPUT_2_NAME):
        output_id = view.get_output_id(name)
        value = view.get_output_value(output_id, key_name="Name")
        assert value is not None, "Device should have a Name value"


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


# ── get_X_value() tests ──────────────────────────────────────────────────────

def test_view_get_device_value_standard_key():
    """get_device_value() should return standard normalized fields by key name."""
    view = smart_device.get_view()
    # "Name" and "Online" are always present in the normalized device dict
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
    assert view.get_output_value(output_id, "Group") is None
    assert view.get_output_value(output_id, "Group", "Ungrouped") == "Ungrouped"


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
    # Voltage, Current, PowerFactor are in the normalized dict but have no dedicated getter
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


# ── Tasmota device tests ─────────────────────────────────────────────────────

TASMOTA_DEVICE_NAME = "Device Test 2"
TASMOTA_DEVICE_ID = 2
TASMOTA_OUTPUT_NAME = "Device 2.Output 1"
TASMOTA_OUTPUT_ID = 3   # Auto-assigned: Shelly outputs claim IDs 1 & 2, so next available is 3
TASMOTA_METER_NAME = "Device 2.Meter 1"
TASMOTA_METER_ID = 3    # Auto-assigned: Shelly meters claim IDs 1 & 2, so next available is 3


def test_tasmota_device_found():
    """Tasmota device should be discoverable via get_device() by name and ID."""
    device = smart_device.get_device(TASMOTA_DEVICE_NAME)
    assert device is not None, "Tasmota device should be found by name"
    assert device.get("ID") == TASMOTA_DEVICE_ID
    assert device.get("Model") == "Tasmota"
    assert device.get("Outputs") == 1
    assert device.get("Meters") == 1
    assert device.get("Inputs") == 0

    device_by_id = smart_device.get_device(TASMOTA_DEVICE_ID)
    assert device_by_id is not None, "Tasmota device should be found by ID"
    assert device_by_id.get("Name") == TASMOTA_DEVICE_NAME


def test_tasmota_device_online():
    """Simulated Tasmota device should report online."""
    device = smart_device.get_device(TASMOTA_DEVICE_NAME)
    assert device.get("Online") is True, "Simulated Tasmota device should be online"
    assert smart_device.is_device_online(TASMOTA_DEVICE_NAME), "is_device_online() should be True"


def test_tasmota_get_device_status():
    """get_device_status() should return True for a simulated Tasmota device."""
    result = smart_device.get_device_status(TASMOTA_DEVICE_NAME)
    assert result is True, "Simulated Tasmota device should return True from get_device_status()"


def test_tasmota_get_output():
    """get_device_component('output', ...) should find the Tasmota output by name and ID."""
    output = smart_device.get_device_component("output", TASMOTA_OUTPUT_NAME)
    assert output is not None, "Tasmota output should be found by name"
    assert output.get("ID") == TASMOTA_OUTPUT_ID
    assert isinstance(output.get("State"), bool), "Output State should be a bool"

    output_by_id = smart_device.get_device_component("output", TASMOTA_OUTPUT_ID)
    assert output_by_id.get("Name") == TASMOTA_OUTPUT_NAME


def test_tasmota_get_meter():
    """get_device_component('meter', ...) should find the Tasmota meter."""
    meter = smart_device.get_device_component("meter", TASMOTA_METER_NAME)
    assert meter is not None, "Tasmota meter should be found by name"
    assert meter.get("ID") == TASMOTA_METER_ID

    meter_by_id = smart_device.get_device_component("meter", TASMOTA_METER_ID)
    assert meter_by_id.get("Name") == TASMOTA_METER_NAME


def test_tasmota_no_inputs_block():
    """Tasmota devices should not expose any input components."""
    # No Inputs: block in config — provider's inputs list should have none for this device
    view = smart_device.get_view()
    snapshot = view.get_json_snapshot()
    # All inputs in the snapshot come from Shelly only
    for inp in snapshot["inputs"]:
        assert inp.get("DeviceID") == DEVICE_ID, "All inputs should belong to the Shelly device"


def test_tasmota_inputs_block_rejected():
    """Initializing with an Inputs: block on a Tasmota device should raise RuntimeError."""
    from sc_smart_device.providers.tasmota_provider import TasmotaProvider

    bad_settings = {
        "Devices": [
            {
                "Name": "Bad Tasmota",
                "Model": "Tasmota",
                "Simulate": True,
                "Inputs": [{"Name": "Should Fail"}],
            }
        ]
    }
    provider = TasmotaProvider(logger)
    with pytest.raises(RuntimeError, match="Inputs"):
        provider.initialize_settings(bad_settings)


def test_tasmota_change_output():
    """change_output() should toggle a Tasmota simulated output."""
    output = smart_device.get_device_component("output", TASMOTA_OUTPUT_NAME)
    current_state = output.get("State")

    result, did_change = smart_device.change_output(TASMOTA_OUTPUT_NAME, not current_state)
    assert result is True, "change_output() should succeed for a simulated Tasmota device"
    assert did_change is True, "Output state should have changed"

    new_state = smart_device.get_device_component("output", TASMOTA_OUTPUT_NAME)["State"]
    assert new_state != current_state, "Output state should be toggled"

    # Restore original state
    smart_device.change_output(TASMOTA_OUTPUT_NAME, current_state)


def test_tasmota_print_device_status():
    """print_device_status() should include the Tasmota device."""
    status_str = smart_device.print_device_status(TASMOTA_DEVICE_NAME)
    assert isinstance(status_str, str), "Status should be a string"
    assert TASMOTA_DEVICE_NAME in status_str, "Status should mention the device name"
    assert "Tasmota" in status_str, "Status should mention the provider model"


def test_tasmota_view_output():
    """SmartDeviceView should include the Tasmota output and allow state read."""
    view = smart_device.get_view()
    output_id = view.get_output_id(TASMOTA_OUTPUT_NAME)
    assert output_id == TASMOTA_OUTPUT_ID, "Tasmota output ID should resolve correctly"
    state = view.get_output_state(output_id)
    assert isinstance(state, bool), "Tasmota output state should be a bool"


def test_tasmota_view_meter():
    """SmartDeviceView should include the Tasmota meter and allow energy/power reads."""
    view = smart_device.get_view()
    meter_id = view.get_meter_id(TASMOTA_METER_NAME)
    assert meter_id == TASMOTA_METER_ID, "Tasmota meter ID should resolve correctly"
    power = view.get_meter_power(meter_id)
    assert isinstance(power, float), "Tasmota meter power should be a float"
    energy = view.get_meter_energy(meter_id)
    assert isinstance(energy, float), "Tasmota meter energy should be a float"


def test_tasmota_view_get_device_value():
    """get_device_value() should work for Tasmota devices through the view."""
    view = smart_device.get_view()
    assert view.get_device_value(TASMOTA_DEVICE_ID, "Name") == TASMOTA_DEVICE_NAME
    assert view.get_device_value(TASMOTA_DEVICE_ID, "Online") is True
    assert view.get_device_value(TASMOTA_DEVICE_ID, "NoSuchKey") is None
    assert view.get_device_value(TASMOTA_DEVICE_ID, "NoSuchKey", "default") == "default"


def test_tasmota_webhooks_not_supported():
    """install_webhook() and does_device_have_webhooks() should reflect Tasmota limitations."""
    device = smart_device.get_device(TASMOTA_DEVICE_NAME)
    assert smart_device.does_device_have_webhooks(device) is False, (
        "Tasmota devices should report no webhook support"
    )
    output = smart_device.get_device_component("output", TASMOTA_OUTPUT_NAME)
    with pytest.raises(RuntimeError):
        smart_device.install_webhook("output.toggle_on", output)
