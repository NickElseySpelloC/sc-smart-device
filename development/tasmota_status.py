"""Basic example of SmartDevice control."""

import platform
import sys
import time

from sc_foundation import SCLogger
from switch_init import switch_init

from sc_smart_device import SCSmartDevice

# ------- Uncomment the relevant section below to test different devices and meters -------

# Test a Tasmota switch
device_names = [
    "Tasmota01",
    "Tasmota02",
    "Tasmota03",
    "Tasmota04"
    ]


def test_status_loop(logger: SCLogger, smart_switch_control: SCSmartDevice) -> None:
    """Test function for basic SmartSwitch control."""
    logger.log_message(f"\n\n\nTesting status query functionality for devices: {device_names}", "summary")
    loop_counter = 1

    # Loop until stopped
    while True:
        # loop through the devices
        for device_name in device_names:
            try:
                device = smart_switch_control.get_device(device_name)
                device_status = smart_switch_control.get_device_status(device)
                if device_status:
                    logger.log_message(f"Device {device_name} is online.", "summary")
                else:
                    logger.log_message(f"get_device_status() returned False: device {device_name}", "error")
                    # sys.exit(1)
            except RuntimeError as e:
                logger.log_message(f"Exception RuntimeError: device {device_name}: {e}", "error")
                sys.exit(1)
            except TimeoutError as e:
                logger.log_message(f"Exception TimeoutError: device {device_name}: {e}", "error")
                sys.exit(1)

            # logger.log_message(f"{device_name} status:\n {smart_switch_control.print_device_status(device_name)}", "detailed")
            time.sleep(0.5)

        print(f"Loop {loop_counter} complete. Waiting 2 seconds...")
        time.sleep(2)
        loop_counter += + 1


def main():
    """Main function to run the example code."""
    print(f"Hello from switch_basic running on {platform.system()}")

    # Initialize the configuration manager, logger, and Smart_switch control
    try:
        _config, logger, smart_switch_control = switch_init()
    except RuntimeError as e:
        print(f"Initialization error: {e}", file=sys.stderr)
        sys.exit(1)

    test_status_loop(logger, smart_switch_control)


if __name__ == "__main__":
    main()
