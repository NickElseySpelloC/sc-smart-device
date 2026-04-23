"""Example of using the SmartDevice control to read temperature sensors."""
import platform
import sys
import time

from sc_foundation import SCLogger
from switch_init import switch_init

from sc_smart_device import SCSmartDevice


def test_temperature(logger: SCLogger, smart_switch_control: SCSmartDevice):  # noqa: PLR0914
    """Test function for temperature SmartDevices control."""
    loop_delay = 5
    loop_count = 0
    max_loops = 20

    device_name = "Sydney Solar"
    pump_output_name = "Sydney Dev A O1"
    roof_probe_name = "Temp Roof"
    pool_probe_name = "Temp Pool Water"

    logger.log_message(f"\n\n\nTesting temperature functionality for device: {device_name}", "summary")

    # Get the device and components
    try:
        device = smart_switch_control.get_device(device_name)
        pump_output = smart_switch_control.get_device_component("output", pump_output_name)
        roof_probe = smart_switch_control.get_device_component("temp_probe", roof_probe_name)
        pool_probe = smart_switch_control.get_device_component("temp_probe", pool_probe_name)
        internal_probe = smart_switch_control.get_device_component("temp_probe", device_name)
    except RuntimeError as e:
        print(f"Error getting device: {e}", file=sys.stderr)
        sys.exit(1)
    except TimeoutError as e:
        print(f"Timeout error getting device: {e}", file=sys.stderr)
        sys.exit(1)
    else:
        while loop_count < max_loops:
            # Refresh the status of all devices
            logger.log_message(f"Refreshing device statuses... (Loop {loop_count + 1}/{max_loops})", "detailed")
            smart_switch_control.refresh_all_device_statuses()

            device_temp = device.get("Temperature", None)
            pump_state = pump_output.get("State")
            roof_probe_id = roof_probe.get("ProbeID", None)
            roof_probe_reading = roof_probe.get("Temperature", None)
            roof_time = roof_probe.get("LastReadingTime", None)

            pool_probe_id = pool_probe.get("ProbeID", None)
            pool_probe_reading = pool_probe.get("Temperature", None)
            pool_time = pool_probe.get("LastReadingTime", None)

            internal_probe_reading = internal_probe.get("Temperature", None)

            logger.log_message(f"{device_name} Temperature: {device_temp}°C.", "detailed")
            logger.log_message(f"{pump_output_name} State: {pump_state}.", "detailed")
            logger.log_message(f"    {roof_probe_name} (ID: {roof_probe_id}) reading: {roof_probe_reading}°C last updated at {roof_time}", "detailed")
            logger.log_message(f"    {pool_probe_name} (ID: {pool_probe_id}) reading: {pool_probe_reading}°C last updated at {pool_time}", "detailed")
            logger.log_message(f"    {device_name} Internal Probe reading: {internal_probe_reading}°C", "detailed")

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

    test_temperature(logger, smart_switch_control)


if __name__ == "__main__":
    main()
