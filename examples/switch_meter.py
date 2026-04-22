"""Example of using the SmartDevice control to read energy meters."""
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

from examples.switch_init import switch_init
from sc_smart_device import SCSmartDevice


def test_new_meter(logger: SCLogger, smart_switch_control: SCSmartDevice):  # noqa: PLR0914
    """Test SmartDevices energy meter functionality."""
    loop_delay = 1
    loop_count = 0
    max_loops = 5

    meter_device_name = "Sydney Panel EM1"
    meter1_name = "Sydney Panel EM1 M1"
    meter2_name = "Sydney Panel EM1 M2"
    output_name = "Sydney Panel EM1 O1"

    logger.log_message(f"Testing meter functionality for device: {meter_device_name}", "summary")

    # Get the device and components
    try:
        meter_device = smart_switch_control.get_device(meter_device_name)
        output = smart_switch_control.get_device_component("output", output_name)
        meter1 = smart_switch_control.get_device_component("meter", meter1_name)
        meter2 = smart_switch_control.get_device_component("meter", meter2_name)
    except RuntimeError as e:
        print(f"Error getting device: {e}", file=sys.stderr)
        sys.exit(1)
    except TimeoutError as e:
        print(f"Timeout error getting device: {e}", file=sys.stderr)
        sys.exit(1)
    else:
        logger.log_message(f"{meter_device_name} status:\n {smart_switch_control.print_device_status(meter_device_name)}", "detailed")

        while loop_count < max_loops:
            # Refresh the status of all devices
            smart_switch_control.get_device_status(meter_device)

            meter1_volts = meter1.get("Voltage", False)
            meter1_power = meter1.get("Power", False)
            meter1_energy = meter1.get("Energy", False)
            meter2_volts = meter2.get("Voltage", False)
            meter2_power = meter2.get("Power", False)
            meter2_energy = meter2.get("Energy", False)

            logger.log_message(f"{output_name} State: {output.get('State', False)}.", "detailed")
            logger.log_message(f"{meter1_name} Volts: {meter1_volts}, Power: {meter1_power}, Energy: {meter1_energy}.", "detailed")
            logger.log_message(f"{meter2_name} Volts: {meter2_volts}, Power: {meter2_power}, Energy: {meter2_energy}.", "detailed")

            time.sleep(loop_delay)
            loop_count += 1


def main():
    """Main function to run the example code."""
    print(f"Hello from sc-utility running on {platform.system()}")

    # Initialize the configuration manager, logger, and SmartDevices control
    try:
        _config, logger, smart_switch_control = switch_init()
    except RuntimeError as e:
        print(f"Initialization error: {e}", file=sys.stderr)
        sys.exit(1)

    test_new_meter(logger, smart_switch_control)


if __name__ == "__main__":
    main()
