"""Manual testing code for the smart_switchControl class."""
# ruff: noqa: E402

import platform
import sys
import time
from pathlib import Path

# Allow running this script directly from a src/ layout checkout.
_project_root = Path(__file__).resolve().parents[1]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
if str(_project_root / "src") not in sys.path:
    sys.path.insert(0, str(_project_root / "src"))

from sc_foundation import SCLogger

from development.switch_init import switch_init
from sc_smart_device import SCSmartDevice, SmartDeviceStatus, SmartDeviceView


def test_basic(logger: SCLogger, smart_switch_control: SCSmartDevice) -> None:
    """Test function for basic Smart_switch control."""
    device_identity = "Sydney Dev A"
    output_identity = "Sydney Dev A O1"
    meter_identity = "Sydney Dev A M1"

    logger.log_message(f"\n\n\nTesting basic functionality for device: {device_identity}", "summary")

    # Get the Smart_switch device
    try:
        device = smart_switch_control.get_device(device_identity)
        device_status = smart_switch_control.get_device_status(device)
        if device_status:
            logger.log_message(f"Device {device_identity} is online.", "summary")
        else:
            logger.log_message(f"Device {device_identity} is offline or not found.", "summary")
    except RuntimeError as e:
        logger.log_message(f"Error getting status for device {device_identity}: {e}", "error")
        sys.exit(1)
    except TimeoutError as e:
        logger.log_message(f"Timeout error getting status for device {device_identity}: {e}", "error")
    else:
        logger.log_message(f"{device_identity} before output change:\n {smart_switch_control.print_device_status(device_identity)}", "detailed")

        # Get the output component and its current state
        output_obj = smart_switch_control.get_device_component("output", output_identity)
        is_online = smart_switch_control.is_device_online(device)
        smart_switch_control.get_device_status(device)
        current_state = output_obj.get("State", False)  # Default to False if State is not found
        logger.log_message(f"#1 Output status for {output_identity}: Is Online: {is_online}, Current State: {current_state}", "detailed")

        # Change the output state to the opposite of the current state
        logger.log_message("Waiting 7 seconds before changing the output state...", "detailed")
        for i in range(7):
            time.sleep(1)  # Short delay to ensure the device is ready for the next command
            print(f"{i + 1}...", end="", flush=True)
        logger.log_message("Attempting to change the output state...", "detailed")
        smart_switch_control.change_output(output_identity, not current_state)

        # Get the meter reading and output status again after the change
        meter_obj = smart_switch_control.get_device_component("meter", meter_identity)
        meter_reading = meter_obj.get("Energy", None)
        logger.log_message(f"Meter reading for {meter_identity}: {meter_reading}", "detailed")

        # Get the latest device status to check if the output change was successful
        is_online = smart_switch_control.is_device_online(device)
        smart_switch_control.get_device_status(device)
        current_state = output_obj.get("State", False)  # Default to False if State is not found
        logger.log_message(f"#2 Output status for {output_identity}: Is Online: {is_online}, Current State: {current_state}", "detailed")

        # Log the full device status after the change
        logger.log_message(f"{device_identity} after output change:\n {smart_switch_control.print_device_status(device_identity)}", "detailed")
        print(smart_switch_control.print_device_status(device_identity))


def main():
    """Main function to run the example code."""
    print(f"Hello from sc-utility running on {platform.system()}")

    # Initialize the configuration manager, logger, and Smart_switch control
    try:
        _config, logger, smart_switch_control = switch_init()
    except RuntimeError as e:
        print(f"Initialization error: {e}", file=sys.stderr)
        sys.exit(1)

    test_basic(logger, smart_switch_control)


if __name__ == "__main__":
    main()
