"""Tasmota device tests — discovery, status, outputs, meters, webhooks."""

import pytest

from sc_smart_device.providers.tasmota_provider import TasmotaProvider

from sc_fixtures import (
    DEVICE_ID,
    TASMOTA_DEVICE_ID,
    TASMOTA_DEVICE_NAME,
    TASMOTA_METER_ID,
    TASMOTA_METER_NAME,
    TASMOTA_OUTPUT_ID,
    TASMOTA_OUTPUT_NAME,
    logger,
    smart_device,
)


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
    """get_device_component('meter', ...) should find the Tasmota meter by name and ID."""
    meter = smart_device.get_device_component("meter", TASMOTA_METER_NAME)
    assert meter is not None, "Tasmota meter should be found by name"
    assert meter.get("ID") == TASMOTA_METER_ID

    meter_by_id = smart_device.get_device_component("meter", TASMOTA_METER_ID)
    assert meter_by_id.get("Name") == TASMOTA_METER_NAME


def test_tasmota_no_inputs_block():
    """Tasmota devices should not expose any input components."""
    view = smart_device.get_view()
    snapshot = view.get_json_snapshot()
    # All inputs in the snapshot come from Shelly only
    for inp in snapshot["inputs"]:
        assert inp.get("DeviceID") == DEVICE_ID, "All inputs should belong to the Shelly device"


def test_tasmota_inputs_block_rejected():
    """Initializing with an Inputs: block on a Tasmota device should raise RuntimeError."""
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
    """print_device_status() should include the Tasmota device name and model."""
    status_str = smart_device.print_device_status(TASMOTA_DEVICE_NAME)
    assert isinstance(status_str, str), "Status should be a string"
    assert TASMOTA_DEVICE_NAME in status_str, "Status should mention the device name"
    assert "Tasmota" in status_str, "Status should mention the provider model"


def test_tasmota_view_output():
    """SmartDeviceView should include the Tasmota output and allow state reads."""
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
