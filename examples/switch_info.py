"""Getting device and model information."""

import platform
import sys

from sc_foundation import SCLogger
from switch_init import switch_init

from sc_smart_device import SCSmartDevice

# ------- Uncomment the relevant section below to test different devices and meters -------
# Test a Shelly switch
device_identity = "Sydney Dev A"

# Test a Tasmota switch
# device_identity = "Sydney Dev B"


def test_info(logger: SCLogger, smart_switch_control: SCSmartDevice) -> None:
    """Test function for basic SmartSwitch control."""
    logger.log_message(f"\n\n\nTesting info functionality for device: {device_identity}", "summary")

    # Get the device
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

        # Log the full device status after the change
        # logger.log_message(f"{device_identity} print_device_status() returns:\n {smart_switch_control.print_device_status(device_identity)}", "detailed")

        # Dump the model library
        model_info = smart_switch_control.print_model_library(mode_str="detailed", provider_id="shelly")
        logger.log_message(f"print_model_library() returns:\n {model_info}", "detailed")


def main():
    """Main function to run the example code."""
    print(f"Hello from switch_basic running on {platform.system()}")

    # Initialize the configuration manager, logger, and Smart_switch control
    try:
        _config, logger, smart_switch_control = switch_init()
    except RuntimeError as e:
        print(f"Initialization error: {e}", file=sys.stderr)
        sys.exit(1)

    test_info(logger, smart_switch_control)


if __name__ == "__main__":
    main()
