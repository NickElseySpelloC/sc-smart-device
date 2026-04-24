"""Worker type definitions for SmartDeviceWorker.

These dataclasses describe the request/result/step protocol used by
[SmartDeviceWorker][sc_smart_device.SmartDeviceWorker].  They are provider-agnostic
and work with any device managed by [SCSmartDevice][sc_smart_device.SCSmartDevice].
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


class StepKind(StrEnum):
    """Step kinds supported by [SmartDeviceWorker][sc_smart_device.SmartDeviceWorker]."""

    CHANGE_OUTPUT = "Change Output State"
    SLEEP = "Sleep"
    REFRESH_STATUS = "Refresh Status"
    GET_LOCATION = "Get Location"


STEP_TYPE_MAP: dict[str, StepKind] = {
    "SLEEP": StepKind.SLEEP,
    "DELAY": StepKind.SLEEP,
    "CHANGE_OUTPUT": StepKind.CHANGE_OUTPUT,
    "REFRESH_STATUS": StepKind.REFRESH_STATUS,
    "GET_LOCATION": StepKind.GET_LOCATION,
}


@dataclass
class DeviceStep:
    """A single step in a `DeviceSequenceRequest`.

    ``params`` keys depend on ``kind``:

    * ``CHANGE_OUTPUT`` — ``{"output_identity": <id|name>, "state": True|False}``
    * ``SLEEP``         — ``{"seconds": <float>}``
    * ``REFRESH_STATUS`` — ``{}``
    * ``GET_LOCATION``  — ``{"device_identity": <id|name>}``
    """

    kind: StepKind
    params: dict[str, Any] = field(default_factory=dict)
    timeout_s: float | None = None
    retries: int = 0
    retry_backoff_s: float = 0.5


@dataclass
class DeviceSequenceResult:
    """Outcome of a completed `DeviceSequenceRequest`."""

    id: str
    ok: bool
    error: str | None = None
    started_ts: float = field(default_factory=time.time)
    finished_ts: float = 0.0


@dataclass
class DeviceSequenceRequest:
    """An ordered list of `DeviceStep` steps to execute as one unit.

    Args:
        steps:       Ordered list of steps to execute.
        id:          Unique request identifier (auto-generated if omitted).
        label:       Human-readable label for logging.
        timeout_s:   Wall-clock budget for the entire sequence (``None`` = unlimited).
        on_complete: Optional callback invoked with the `DeviceSequenceResult`
                     after the sequence finishes (success or failure).
    """

    steps: list[DeviceStep]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    label: str = ""
    timeout_s: float | None = None
    on_complete: Callable[[DeviceSequenceResult], None] | None = None
