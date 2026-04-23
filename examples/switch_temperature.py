"""Example of using the SmartDevice control to read temperature sensors."""
import platform
import sys
import time

from sc_foundation import SCLogger
from switch_init import switch_init

from sc_smart_device import SCSmartDevice

# ------- Uncomment the relevant section below to test different devices and meters -------
# Test a Shelly switch with add-on temperature probes
device_name = "Sydney Dev A"
output_name = "Sydney Dev A O1"
has_external_probes = False
ext_temp_probe_name1 = "Temp Roof"
ext_temp_probe_name2 = "Temp Pool Water"

# Test a Tasmota switch including internal temperature probe
# device_name = "Sydney Dev B"
# output_name = "Sydney Dev B O1"
# has_external_probes = False
# ext_temp_probe_name1 = ""
# ext_temp_probe_name2 = ""


def test_temperature(logger: SCLogger, smart_switch_control: SCSmartDevice):  # noqa: PLR0914
    """Test function for temperature SmartDevices control."""
    loop_delay = 5
    loop_count = 0
    max_loops = 20

    logger.log_message(f"\n\n\nTesting temperature functionality for device: {device_name}", "summary")

    # Get the device and components
    try:
        device = smart_switch_control.get_device(device_name)
        output = smart_switch_control.get_device_component("output", output_name)
        internal_probe = smart_switch_control.get_device_component("temp_probe", device_name)
        if has_external_probes:
            temp_probe1 = smart_switch_control.get_device_component("temp_probe", ext_temp_probe_name1)
            temp_probe2 = smart_switch_control.get_device_component("temp_probe", ext_temp_probe_name2)
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
            output_state = output.get("State")

            internal_probe_reading = internal_probe.get("Temperature", None)

            logger.log_message(f"{device_name} Temperature: {device_temp}°C.", "detailed")
            logger.log_message(f"{output_name} State: {output_state}.", "detailed")
            logger.log_message(f"    {device_name} Internal Probe reading: {internal_probe_reading}°C", "detailed")

            if has_external_probes:
                temp_probe1_id = temp_probe1.get("ProbeID", None)
                temp_probe1_reading = temp_probe1.get("Temperature", None)
                temp_probe1_time = temp_probe1.get("LastReadingTime", None)

                temp_probe2_id = temp_probe2.get("ProbeID", None)
                temp_probe2_reading = temp_probe2.get("Temperature", None)
                temp_probe2_time = temp_probe2.get("LastReadingTime", None)

                logger.log_message(f"    {ext_temp_probe_name1} (ID: {temp_probe1_id}) reading: {temp_probe1_reading}°C last updated at {temp_probe1_time}", "detailed")
                logger.log_message(f"    {ext_temp_probe_name2} (ID: {temp_probe2_id}) reading: {temp_probe2_reading}°C last updated at {temp_probe2_time}", "detailed")

            time.sleep(loop_delay)
            loop_count += 1


def main():
    """Main function to run the example code."""
    print(f"Hello from switch_temperature running on {platform.system()}")

    # Initialize the configuration manager, logger, and SmartDevices control
    try:
        _config, logger, smart_switch_control = switch_init()
    except RuntimeError as e:
        print(f"Initialization error: {e}", file=sys.stderr)
        sys.exit(1)

    test_temperature(logger, smart_switch_control)


if __name__ == "__main__":
    main()
