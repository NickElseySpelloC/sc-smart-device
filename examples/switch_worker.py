"""Example demonstrating SmartDeviceWorker for sequenced device control.

SmartDeviceWorker runs a background thread that processes
DeviceSequenceRequest jobs.  Each job is an ordered list of DeviceStep
steps (REFRESH_STATUS, CHANGE_OUTPUT, SLEEP, GET_LOCATION).  The main
thread submits a request, optionally waits for it to finish, then reads
the latest device state from a SmartDeviceView snapshot.

This example submits a single sequence that:
  1. Refreshes status for all devices
  2. Turns Sydney Dev A O1 ON
  3. Waits 5 seconds
  4. Turns Sydney Dev B O1 ON
  5. Waits 5 seconds
  6. Turns Sydney Dev A O1 OFF
  7. Waits 5 seconds
  8. Turns Sydney Dev B O1 OFF
"""

import platform
import sys
import threading

from sc_foundation import SCLogger
from switch_init import switch_init

from sc_smart_device import (
    DeviceSequenceRequest,
    DeviceStep,
    SCSmartDevice,
    SmartDeviceView,
    SmartDeviceWorker,
    StepKind,
)

# Output names as defined in switch_config.yaml
OUTPUT_A = "Sydney Dev A O1"
OUTPUT_B = "Sydney Dev B O1"


def print_view_summary(logger: SCLogger, view: SmartDeviceView) -> None:
    """Log a one-line status summary for each device using a SmartDeviceView snapshot.

    Args:
        logger: SCLogger instance.
        view: Frozen SmartDeviceView snapshot to read from.
    """
    snapshot = view.get_json_snapshot()
    for device in snapshot["devices"]:
        device_id = device["ID"]
        name = device.get("Name", f"Device {device_id}")
        online = view.get_device_online(device_id)

        # Collect output states for this device
        output_states = []
        for output in snapshot["outputs"]:
            if output.get("DeviceID") == device_id:
                output_states.append(f"{output['Name']}={'ON' if output.get('State') else 'OFF'}")

        state_str = ", ".join(output_states) if output_states else "no outputs"
        logger.log_message(
            f"  {name}: online={online}  |  {state_str}",
            "summary",
        )


def create_worker(logger: SCLogger, smart_switch_control: SCSmartDevice) -> tuple[SmartDeviceWorker, threading.Thread]:
    """Wake_event is set by the worker after every completed request, which allows a main-loop thread to react without polling.

    Args:
        logger: SCLogger instance.
        smart_switch_control: SCSmartDevice instance to control.

    Returns:
        A tuple of (SmartDeviceWorker instance, worker thread) for the caller to manage.
    """
    wake_event = threading.Event()
    worker = SmartDeviceWorker(
        smart_device=smart_switch_control,
        logger=logger,
        wake_event=wake_event,
    )

    worker_thread = threading.Thread(target=worker.run, daemon=True, name="device-worker")
    worker_thread.start()
    logger.log_message("Worker thread started.", "detailed")

    return worker, worker_thread


def build_sequence() -> DeviceSequenceRequest:
    """Build the DeviceSequenceRequest defining the steps to execute.

    Steps execute in order within a single request.  The worker guarantees
    each step finishes (or exhausts its retries) before the next begins.

    Returns:
        A DeviceSequenceRequest instance with the desired steps and parameters.
    """
    steps = [
        # Step 1: refresh status so our initial snapshot is up to date
        DeviceStep(StepKind.REFRESH_STATUS),

        # Step 2: turn Sydney Dev A O1 on
        DeviceStep(
            StepKind.CHANGE_OUTPUT,
            {"output_identity": OUTPUT_A, "state": True},
            retries=1,
            retry_backoff_s=2.0,
        ),

        # Step 3: wait 5 seconds
        DeviceStep(StepKind.SLEEP, {"seconds": 5}),

        # Step 4: turn Sydney Dev B O1 on
        DeviceStep(
            StepKind.CHANGE_OUTPUT,
            {"output_identity": OUTPUT_B, "state": True},
            retries=1,
            retry_backoff_s=2.0,
        ),

        # Step 5: wait 5 seconds
        DeviceStep(StepKind.SLEEP, {"seconds": 5}),

        # Step 6: turn Sydney Dev A O1 off
        DeviceStep(
            StepKind.CHANGE_OUTPUT,
            {"output_identity": OUTPUT_A, "state": False},
            retries=1,
            retry_backoff_s=2.0,
        ),

        # Step 7: wait 5 seconds
        DeviceStep(StepKind.SLEEP, {"seconds": 5}),

        # Step 8: turn Sydney Dev B O1 off
        DeviceStep(
            StepKind.CHANGE_OUTPUT,
            {"output_identity": OUTPUT_B, "state": False},
            retries=1,
            retry_backoff_s=2.0,
        ),
    ]

    req = DeviceSequenceRequest(
        steps=steps,
        label="switch_worker_demo",
        timeout_s=60.0,
    )
    return req


def run_sequence(logger: SCLogger, smart_switch_control: SCSmartDevice, worker: SmartDeviceWorker, sequence_req: DeviceSequenceRequest) -> None:
    """Build and run the demonstration sequence via SmartDeviceWorker.

    Args:
        logger: SCLogger instance.
        smart_switch_control: SCSmartDevice instance to control.
        worker: SmartDeviceWorker instance to submit the sequence to.
        sequence_req: DeviceSequenceRequest defining the steps to execute.
    """
    logger.log_message("\n\n\nStarting SmartDeviceWorker sequence example", "summary")

    # ── Show initial state ───────────────────────────────────────────────────
    logger.log_message("Initial device state (from worker snapshot):", "summary")
    print_view_summary(logger, worker.get_latest_status())

    # ── Submit and wait ───────────────────────────────────────────────────────
    logger.log_message(
        f"Submitting sequence '{sequence_req.label}' ({len(sequence_req.steps)} steps)...", "summary"
    )
    req_id = worker.submit(sequence_req)

    # Block until the sequence finishes or the overall timeout expires.
    # We add a small buffer beyond the sequence timeout_s for safety.
    wait_timeout = (sequence_req.timeout_s or 60.0) + 5.0
    completed = worker.wait_for_result(req_id, timeout=wait_timeout)

    # ── Collect and report the result ─────────────────────────────────────────
    result = worker.get_result(req_id)

    if not completed or result is None:
        logger.log_message("Sequence timed out waiting for a result.", "error")
    elif result.ok:
        elapsed = result.finished_ts - result.started_ts
        logger.log_message(
            f"Sequence '{sequence_req.label}' completed successfully in {elapsed:.1f}s.", "summary"
        )
    else:
        logger.log_message(
            f"Sequence '{sequence_req.label}' failed: {result.error}", "error"
        )

    # ── Show final state via SmartDeviceView ──────────────────────────────────
    # get_latest_status() returns the frozen snapshot saved after the last
    # REFRESH_STATUS step (the first step in our sequence).  For the very
    # latest state after the output changes, call get_view() directly.
    smart_switch_control.refresh_all_device_statuses()
    final_view: SmartDeviceView = smart_switch_control.get_view()

    logger.log_message("Final device state (from fresh view):", "summary")
    print_view_summary(logger, final_view)


def shutdown_worker(logger: SCLogger, worker: SmartDeviceWorker, worker_thread: threading.Thread) -> None:
    """Cleanly shut down the worker thread."""
    worker.stop()
    worker_thread.join(timeout=5)
    logger.log_message("Worker thread stopped.", "detailed")


def main() -> None:
    """Main entry point for the switch_worker example."""
    print(f"Hello from switch_worker running on {platform.system()}")

    try:
        _config, logger, smart_switch_control = switch_init()
    except RuntimeError as e:
        print(f"Initialization error: {e}", file=sys.stderr)
        sys.exit(1)

    worker, worker_thread = create_worker(logger, smart_switch_control)

    sequence_req = build_sequence()

    run_sequence(logger, smart_switch_control, worker=worker, sequence_req=sequence_req)

    shutdown_worker(logger, worker, worker_thread)


if __name__ == "__main__":
    main()
