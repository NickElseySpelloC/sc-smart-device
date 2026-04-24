"""SmartDeviceWorker tests — submit, wait, result, callback, multi-step, stop."""

import threading

from sc_smart_device import (
    DeviceSequenceRequest,
    DeviceSequenceResult,
    DeviceStep,
    SmartDeviceView,
    SmartDeviceWorker,
    STEP_TYPE_MAP,
    StepKind,
)

from sc_fixtures import (
    DEVICE_CLIENTNAME,
    TASMOTA_OUTPUT_NAME,
    logger,
    smart_device,
)

# ── Module-level worker (shared across all tests in this file) ────────────────
# A single worker thread handles the queue for all tests.  Tests that need
# isolation spin up their own temporary worker (see test_worker_stop).

_worker_wake_event = threading.Event()
_worker = SmartDeviceWorker(smart_device, logger, _worker_wake_event)
_worker_thread = threading.Thread(target=_worker.run, daemon=True, name="test-worker")
_worker_thread.start()


# ── Type / enum tests ────────────────────────────────────────────────────────

def test_worker_types_exported():
    """StepKind, STEP_TYPE_MAP, DeviceStep, DeviceSequenceRequest and DeviceSequenceResult should all import cleanly."""
    assert StepKind.REFRESH_STATUS == "Refresh Status"
    assert StepKind.CHANGE_OUTPUT == "Change Output State"
    assert StepKind.SLEEP == "Sleep"
    assert StepKind.GET_LOCATION == "Get Location"

    assert "SLEEP" in STEP_TYPE_MAP
    assert "DELAY" in STEP_TYPE_MAP
    assert STEP_TYPE_MAP["DELAY"] == StepKind.SLEEP
    assert STEP_TYPE_MAP["CHANGE_OUTPUT"] == StepKind.CHANGE_OUTPUT
    assert STEP_TYPE_MAP["REFRESH_STATUS"] == StepKind.REFRESH_STATUS
    assert STEP_TYPE_MAP["GET_LOCATION"] == StepKind.GET_LOCATION


def test_worker_device_step_defaults():
    """DeviceStep should default params to {} and retries to 0."""
    step = DeviceStep(StepKind.SLEEP)
    assert step.params == {}
    assert step.retries == 0
    assert step.retry_backoff_s == 0.5
    assert step.timeout_s is None

    step_with_params = DeviceStep(StepKind.SLEEP, {"seconds": 0.1})
    assert step_with_params.params == {"seconds": 0.1}


def test_worker_sequence_request_auto_id():
    """DeviceSequenceRequest should auto-generate a unique UUID id."""
    req1 = DeviceSequenceRequest(steps=[DeviceStep(StepKind.REFRESH_STATUS)])
    req2 = DeviceSequenceRequest(steps=[DeviceStep(StepKind.REFRESH_STATUS)])
    assert req1.id != req2.id, "Each request should get a unique auto-generated id"
    assert req1.label == ""
    assert req1.timeout_s is None
    assert req1.on_complete is None


# ── Initialisation ────────────────────────────────────────────────────────────

def test_worker_init():
    """SmartDeviceWorker should initialize and immediately provide a view snapshot."""
    assert isinstance(_worker, SmartDeviceWorker), "Worker should be a SmartDeviceWorker"
    view = _worker.get_latest_status()
    assert isinstance(view, SmartDeviceView), "get_latest_status() should return a SmartDeviceView"


# ── REFRESH_STATUS ────────────────────────────────────────────────────────────

def test_worker_submit_refresh_status():
    """Submitting a REFRESH_STATUS step should complete successfully."""
    req = DeviceSequenceRequest(
        steps=[DeviceStep(StepKind.REFRESH_STATUS)],
        label="test_refresh",
    )
    req_id = _worker.submit(req)
    assert req_id == req.id, "submit() should return the request id"

    completed = _worker.wait_for_result(req_id, timeout=10)
    assert completed, "REFRESH_STATUS step should complete within 10 seconds"

    result = _worker.get_result(req_id)
    assert isinstance(result, DeviceSequenceResult), "Result should be a DeviceSequenceResult"
    assert result.ok is True, f"REFRESH_STATUS should succeed; error={result.error}"
    assert result.finished_ts > result.started_ts, "finished_ts should be after started_ts"


def test_worker_latest_status_updated_after_refresh():
    """After a successful REFRESH_STATUS, get_latest_status() should return a fresh view."""
    req_id = _worker.request_refresh_status()
    _worker.wait_for_result(req_id, timeout=10)

    view = _worker.get_latest_status()
    assert isinstance(view, SmartDeviceView)
    assert view.all_devices_online(), "All simulated devices should be online after refresh"


# ── SLEEP ─────────────────────────────────────────────────────────────────────

def test_worker_submit_sleep():
    """A short SLEEP step should succeed and take at least the requested time."""
    req = DeviceSequenceRequest(
        steps=[DeviceStep(StepKind.SLEEP, {"seconds": 0.1})],
        label="test_sleep",
    )
    req_id = _worker.submit(req)
    completed = _worker.wait_for_result(req_id, timeout=5)
    assert completed, "SLEEP step should complete within 5 seconds"

    result = _worker.get_result(req_id)
    assert result is not None
    assert result.ok is True, f"SLEEP step should succeed; error={result.error}"
    elapsed = result.finished_ts - result.started_ts
    assert elapsed >= 0.1, f"Elapsed time ({elapsed:.3f}s) should be ≥ 0.1 s"


# ── CHANGE_OUTPUT ─────────────────────────────────────────────────────────────

def test_worker_submit_change_output():
    """A CHANGE_OUTPUT step should toggle a simulated output successfully."""
    output_name = "Device 1.Output 1"
    output = smart_device.get_device_component("output", output_name)
    current_state = output.get("State")
    new_state = not current_state

    req = DeviceSequenceRequest(
        steps=[
            DeviceStep(
                StepKind.CHANGE_OUTPUT,
                {"output_identity": output_name, "state": new_state},
            )
        ],
        label="test_change_output",
    )
    req_id = _worker.submit(req)
    completed = _worker.wait_for_result(req_id, timeout=10)
    assert completed, "CHANGE_OUTPUT step should complete within 10 seconds"

    result = _worker.get_result(req_id)
    assert result is not None
    assert result.ok is True, f"CHANGE_OUTPUT step should succeed; error={result.error}"

    updated_output = smart_device.get_device_component("output", output_name)
    assert updated_output.get("State") == new_state, "Output state should reflect the change"

    # Restore original state
    smart_device.change_output(output_name, current_state)


# ── on_complete callback ──────────────────────────────────────────────────────

def test_worker_on_complete_callback():
    """on_complete callback should be called exactly once with the completed result."""
    callback_results: list[DeviceSequenceResult] = []

    def capture(res: DeviceSequenceResult) -> None:
        callback_results.append(res)

    req = DeviceSequenceRequest(
        steps=[DeviceStep(StepKind.REFRESH_STATUS)],
        label="test_callback",
        on_complete=capture,
    )
    req_id = _worker.submit(req)
    _worker.wait_for_result(req_id, timeout=10)

    assert len(callback_results) == 1, "on_complete should have been called exactly once"
    assert callback_results[0].id == req_id
    assert callback_results[0].ok is True


# ── Multi-step sequence ────────────────────────────────────────────────────────

def test_worker_multi_step_sequence():
    """A sequence with multiple steps should execute them all in order."""
    output_name = TASMOTA_OUTPUT_NAME
    output = smart_device.get_device_component("output", output_name)
    original_state = output.get("State")

    req = DeviceSequenceRequest(
        steps=[
            DeviceStep(StepKind.CHANGE_OUTPUT, {"output_identity": output_name, "state": True}),
            DeviceStep(StepKind.SLEEP, {"seconds": 0.05}),
            DeviceStep(StepKind.CHANGE_OUTPUT, {"output_identity": output_name, "state": False}),
            DeviceStep(StepKind.REFRESH_STATUS),
        ],
        label="test_multi_step",
        timeout_s=15.0,
    )
    req_id = _worker.submit(req)
    completed = _worker.wait_for_result(req_id, timeout=15)
    assert completed, "Multi-step sequence should complete within 15 seconds"

    result = _worker.get_result(req_id)
    assert result is not None
    assert result.ok is True, f"Multi-step sequence should succeed; error={result.error}"

    # After the sequence the output should be OFF (last CHANGE_OUTPUT set False)
    updated_output = smart_device.get_device_component("output", output_name)
    assert updated_output.get("State") is False, "Tasmota output should be False after sequence"

    # Restore
    smart_device.change_output(output_name, original_state)


# ── wake_event ────────────────────────────────────────────────────────────────

def test_worker_wake_event_set_after_request():
    """wake_event should be set after a request completes."""
    _worker_wake_event.clear()
    req_id = _worker.request_refresh_status()
    _worker.wait_for_result(req_id, timeout=10)
    assert _worker_wake_event.is_set(), "wake_event should be set after request completion"


# ── Unknown request id ────────────────────────────────────────────────────────

def test_worker_wait_for_unknown_id():
    """wait_for_result() on an unknown id should return True immediately."""
    result = _worker.wait_for_result("no-such-id", timeout=1)
    assert result is True, "Unknown request id should be considered done"


def test_worker_get_result_unknown_id():
    """get_result() on an unknown id should return None."""
    result = _worker.get_result("no-such-id")
    assert result is None, "Unknown request id should return None from get_result()"


# ── GET_LOCATION ──────────────────────────────────────────────────────────────

def test_worker_request_device_location():
    """request_device_location() should submit successfully (returns None for simulated devices)."""
    req_id = _worker.request_device_location(DEVICE_CLIENTNAME)
    completed = _worker.wait_for_result(req_id, timeout=10)
    assert completed, "Location request should complete within 10 seconds"
    result = _worker.get_result(req_id)
    assert result is not None
    assert result.ok is True, f"Location request should succeed; error={result.error}"


# ── stop() ────────────────────────────────────────────────────────────────────

def test_worker_stop():
    """stop() should signal the worker loop to exit cleanly."""
    wake = threading.Event()
    temp_worker = SmartDeviceWorker(smart_device, logger, wake)
    thread = threading.Thread(target=temp_worker.run, daemon=True)
    thread.start()
    assert thread.is_alive(), "Worker thread should be running"

    temp_worker.stop()
    thread.join(timeout=5)
    assert not thread.is_alive(), "Worker thread should have stopped within 5 seconds"
