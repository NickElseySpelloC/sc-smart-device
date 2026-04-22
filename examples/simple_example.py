"""Example code using the sc_utility libraries. Should not be included in the distrbution."""
# ruff: noqa: E402

import platform
import sys
import threading
from pathlib import Path

from mergedeep import merge

# Allow running this script directly from a src/ layout checkout.
_project_root = Path(__file__).resolve().parents[1]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
if str(_project_root / "src") not in sys.path:
    sys.path.insert(0, str(_project_root / "src"))

from sc_foundation import SCConfigManager, SCLogger

from examples.validation_extras import smart_switch_extra_validation
from sc_smart_device import SCSmartDevice, smart_devices_validator

CONFIG_FILE = "examples/switch_config.yaml"


def main():  # noqa: PLR0914, PLR0915
    device_identity = "Sydney Dev A"
    output_identity = "Sydney Dev A O1"

    loop_delay = 5
    loop_count = 0
    max_loops = 20
    wake_event = threading.Event()

    print(f"Hello from simple_example running on {platform.system()}")

    # Merge the SmartDevices validation schema with the default validation schema
    merged_schema = merge({}, smart_devices_validator, smart_switch_extra_validation)
    assert isinstance(merged_schema, dict), "Merged schema should be type dict"

    # Initialize the SC_ConfigManager class
    try:
        config = SCConfigManager(config_file=CONFIG_FILE, validation_schema=merged_schema)
    except RuntimeError as e:
        print(f"Configuration file error: {e}", file=sys.stderr)
        return

    # Initialize the SC_Logger class
    try:
        logger = SCLogger(config.get_logger_settings())
    except RuntimeError as e:
        print(f"Logger initialisation error: {e}", file=sys.stderr)
        return

    smart_switch_settings = config.get("SCSmartDevices")

    if smart_switch_settings is None:
        error_msg = "No SmartDevices settings found in the configuration file."
        raise RuntimeError(error_msg)

    # Initialize the SCSmartDevice class
    try:
        smart_switch_control = SCSmartDevice(logger, smart_switch_settings, wake_event)
    except RuntimeError as e:
        error_msg = f"SCSmartDevice initialization error: {e}"
        raise RuntimeError(error_msg) from e
    logger.log_message(f"SCSmartDevice initialized successfully with {len(smart_switch_control.devices)} devices.", "summary")

    # Print the model library
    print(f"Print brief version of model library:\n {smart_switch_control.print_model_library(mode_str='brief')}")

    # Print the list of devices as configured in the config file
    print(f"Print all devices:\n {smart_switch_control.print_device_status()}")

    # Get a device
    try:
        device = smart_switch_control.get_device(device_identity)
    except (RuntimeError, TimeoutError) as e:
        print(e, file=sys.stderr)
    else:
        print(f"Device {device_identity} model: {device.get('Model', 'Unknown')}")
        print(f"Device {device_identity} is {'online' if device.get('Online', False) else 'offline'}.")

    # Change the output of a device
    output = smart_switch_control.get_device_component("output", output_identity)
    current_state = output["State"]
    result, did_change = smart_switch_control.change_output(output_identity, not current_state)
    print(f"Output {output_identity} changed: {did_change}, Result: {result}")

    # Loop and listed for webhook events
    while loop_count < max_loops:  # noqa: PLR1702
        print(f"Starting loop {loop_count + 1}/{max_loops}")

        # Do application stuff here

        # Wait for a webhook event or timeout
        wake_event.wait(timeout=loop_delay)
        if wake_event.is_set():
            try:
                # We were woken by a webhook call
                event = smart_switch_control.pull_webhook_event()
                if event:
                    print(f"Received webhook event: {event.get('Event')}")
                    if event.get("Event") in {"input.toggle_on", "input.toggle_off"}:
                        # An input was toggled on/off, change the corresponding output
                        output_identity = event.get("Component")
                        if not output_identity:
                            print(f"Unable to get component object for event: {event}", file=sys.stderr)
                            continue
                        new_state = event.get("Event") == "input.toggle_on"
                        result, did_change = smart_switch_control.change_output(output_identity, new_state)
                        print(f"Output {output_identity} changed: {did_change}, Result: {result}")
            except (AttributeError, RuntimeError) as e:
                print(f"Error processing webhook event: {e}", file=sys.stderr)
            wake_event.clear()
        loop_count += 1


if __name__ == "__main__":
    main()
