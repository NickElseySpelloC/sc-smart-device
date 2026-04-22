"""Manual testing code demonstrating SmartDeviceView for reading device state."""
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
from sc_smart_device import SCSmartDevice, SmartDeviceView


def test_view(logger: SCLogger, smart_switch_control: SCSmartDevice) -> None:
    """Test function demonstrating SmartDeviceView for reading device state.

    SmartDeviceView is a frozen, indexed snapshot — ideal for multi-threaded
    apps where you want a consistent read without holding a lock.

    Pattern:
      1. Refresh device state via smart_switch_control (mutable side)
      2. Call get_view() to take a new frozen snapshot
      3. Read all state from the view (no dict access needed)
    """
    device_name = "Sydney Dev A"
    output_name = "Sydney Dev A O1"
    meter_name = "Sydney Dev A M1"

    logger.log_message(f"\n\n\nTesting SmartDeviceView for device: {device_name}", "summary")

    # ── Initial status refresh ───────────────────────────────────────────────
    try:
        device = smart_switch_control.get_device(device_name)
        device_status = smart_switch_control.get_device_status(device)
        if device_status:
            logger.log_message(f"Device {device_name} is online.", "summary")
        else:
            logger.log_message(f"Device {device_name} is offline or not found.", "summary")
    except RuntimeError as e:
        logger.log_message(f"Error getting status for device {device_name}: {e}", "error")
        sys.exit(1)
    except TimeoutError as e:
        logger.log_message(f"Timeout error getting status for device {device_name}: {e}", "error")
        return

    logger.log_message(
        f"{device_name} before output change:\n {smart_switch_control.print_device_status(device_name)}",
        "detailed",
    )

    # ── Snapshot #1 — read state before the output change ───────────────────
    # get_view() returns a frozen snapshot of the current provider state.
    # Resolve names → IDs once; use IDs for all subsequent lookups.
    view: SmartDeviceView = smart_switch_control.get_view()

    device_id = view.get_device_id(device_name)
    output_id = view.get_output_id(output_name)
    meter_id = view.get_meter_id(meter_name)

    is_online = view.get_device_online(device_id)
    current_state = view.get_output_state(output_id)
    logger.log_message(
        f"#1 Output status for {output_name}: Is Online: {is_online}, Current State: {current_state}",
        "detailed",
    )

    # ── Output change (control still goes through smart_switch_control) ──────
    logger.log_message("Waiting 7 seconds before changing the output state...", "detailed")
    for i in range(7):
        time.sleep(1)
        print(f"{i + 1}...", end="", flush=True)
    print()

    logger.log_message("Attempting to change the output state...", "detailed")
    smart_switch_control.change_output(output_name, not current_state)

    # ── Snapshot #2 — refresh then take a new view ───────────────────────────
    # The view is frozen at the moment it was created, so we need a fresh one
    # after any state-changing operation or device refresh.
    smart_switch_control.get_device_status(device)
    view = smart_switch_control.get_view()

    is_online = view.get_device_online(device_id)
    current_state = view.get_output_state(output_id)
    meter_energy = view.get_meter_energy(meter_id)
    meter_power = view.get_meter_power(meter_id)

    logger.log_message(f"Meter reading for {meter_name}: energy={meter_energy} Wh, power={meter_power} W", "detailed")
    logger.log_message(
        f"#2 Output status for {output_name}: Is Online: {is_online}, Current State: {current_state}",
        "detailed",
    )

    logger.log_message(
        f"{device_name} after output change:\n {smart_switch_control.print_device_status(device_name)}",
        "detailed",
    )
    print(smart_switch_control.print_device_status(device_name))


def main():
    """Main function to run the SmartDeviceView example."""
    print(f"Hello from sc-smart-device running on {platform.system()}")

    try:
        _config, logger, smart_switch_control = switch_init()
    except RuntimeError as e:
        print(f"Initialization error: {e}", file=sys.stderr)
        sys.exit(1)

    test_view(logger, smart_switch_control)


if __name__ == "__main__":
    main()
