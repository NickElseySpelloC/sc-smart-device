"""Basic SCSmartDevice tests — get_device, status, change_output, etc."""

import sys

from sc_smart_device import SCSmartDevice

from sc_fixtures import (
    DEVICE_CLIENTNAME,
    config,
    logger,
    smart_device,
)


def test_get_device():
    """get_device() should find a Shelly device by name and return correct metadata."""
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
        assert device.get("Meters") == 2, "Device meter count should be 2"


def test_get_device_information():
    """get_device_information() should return the device dict augmented with component sub-lists."""
    try:
        device = smart_device.get_device(DEVICE_CLIENTNAME)
        device_info = smart_device.get_device_information(device)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    else:
        assert device_info is not None, f"Device {DEVICE_CLIENTNAME} information should be found"
        assert isinstance(device_info, dict), f"Device {DEVICE_CLIENTNAME} information should be a dict"
        assert device_info.get("Model") == "Shelly2PMG3", "Device information should contain model"
        assert len(device_info.get("Inputs")) == 2, "Device information should contain 2 inputs"  # type: ignore[arg-type]
        assert len(device_info.get("Outputs")) == 2, "Device information should contain 2 outputs"  # type: ignore[arg-type]
        assert len(device_info.get("Meters")) == 2, "Device information should contain 2 meters"  # type: ignore[arg-type]


def test_get_device_status():
    """get_device_status() should update component states and return True for a simulated device."""
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

    device_meter = smart_device.get_device_component("meter", "Meter 1")  # Auto-generated name
    assert device_meter is not None, "Device meter should be found"


def test_refresh_all_device_statuses():
    """refresh_all_device_statuses() should run without error."""
    try:
        smart_device.refresh_all_device_statuses()
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def test_is_device_online():
    """is_device_online() should return True for a simulated device."""
    try:
        is_online = smart_device.is_device_online(DEVICE_CLIENTNAME)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    else:
        assert is_online, f"Device {DEVICE_CLIENTNAME} should be online"


def test_print_device_status():
    """print_device_status() should return a non-empty string containing generation info."""
    try:
        device_status = smart_device.print_device_status(DEVICE_CLIENTNAME)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    else:
        assert device_status is not None, f"Device {DEVICE_CLIENTNAME} status should be printed"
        assert isinstance(device_status, str), f"Device {DEVICE_CLIENTNAME} status should be a string"
        assert device_status.find("Generation: ") != -1, "Device status should contain generation info"


def test_print_model_library():
    """print_model_library() should include the Shelly2PMG3 model."""
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
    """change_output() should toggle an output and return (True, True)."""
    output_identity = "Device 1.Output 1"
    try:
        output_obj = smart_device.get_device_component("output", output_identity)
        current_state = output_obj["State"]
        result, did_change = smart_device.change_output(output_identity, not current_state)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    else:
        assert result, f"Output {output_identity} state should change successfully"
        assert did_change, f"Output {output_identity} state should have changed"
        new_state = smart_device.get_device_component("output", output_identity)["State"]
        assert new_state != current_state, "Output state should be toggled"
