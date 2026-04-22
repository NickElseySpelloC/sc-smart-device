from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, NoReturn

if TYPE_CHECKING:
    import datetime as dt

    from sc_smart_device.models.smart_device_status import SmartDeviceStatus


@dataclass(frozen=True)  # noqa: PLR0904
class SmartDeviceView:
    """Read-only facade over a SmartDeviceStatus snapshot.

    Provides efficient ID-based lookups for all component types.
    Build a SmartDeviceView from a SmartDeviceStatus via SCSmartDevice.get_view().
    """

    snapshot: SmartDeviceStatus

    _device_name_to_id: dict[str, int] = field(init=False, repr=False)
    _output_name_to_id: dict[str, int] = field(init=False, repr=False)
    _input_name_to_id: dict[str, int] = field(init=False, repr=False)
    _meter_name_to_id: dict[str, int] = field(init=False, repr=False)
    _temp_probe_name_to_id: dict[str, int] = field(init=False, repr=False)

    _devices_by_id: dict[int, dict[str, Any]] = field(init=False, repr=False)
    _outputs_by_id: dict[int, dict[str, Any]] = field(init=False, repr=False)
    _inputs_by_id: dict[int, dict[str, Any]] = field(init=False, repr=False)
    _meters_by_id: dict[int, dict[str, Any]] = field(init=False, repr=False)
    _temp_probes_by_id: dict[int, dict[str, Any]] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_device_name_to_id", self._build_name_index(self.snapshot.devices))
        object.__setattr__(self, "_output_name_to_id", self._build_name_index(self.snapshot.outputs))
        object.__setattr__(self, "_input_name_to_id", self._build_name_index(self.snapshot.inputs))
        object.__setattr__(self, "_meter_name_to_id", self._build_name_index(self.snapshot.meters))
        object.__setattr__(self, "_temp_probe_name_to_id", self._build_name_index(self.snapshot.temp_probes))

        object.__setattr__(self, "_devices_by_id", self._build_id_index(self.snapshot.devices))
        object.__setattr__(self, "_outputs_by_id", self._build_id_index(self.snapshot.outputs))
        object.__setattr__(self, "_inputs_by_id", self._build_id_index(self.snapshot.inputs))
        object.__setattr__(self, "_meters_by_id", self._build_id_index(self.snapshot.meters))
        object.__setattr__(self, "_temp_probes_by_id", self._build_id_index(self.snapshot.temp_probes))

    @staticmethod
    def _build_name_index(items: list[dict[str, Any]]) -> dict[str, int]:
        return {item["Name"]: item["ID"] for item in items if "Name" in item and "ID" in item}

    @staticmethod
    def _build_id_index(items: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
        return {item["ID"]: item for item in items if "ID" in item}

    @staticmethod
    def _raise_index_error(message: str) -> NoReturn:
        raise IndexError(message)

    # ── Device lookups ──────────────────────────────────────────────────────

    def get_device_id_list(self) -> list[int]:
        return list(self._devices_by_id.keys())

    def validate_device_id(self, device_id: int | str) -> bool:
        if isinstance(device_id, str):
            return self.get_device_id(device_id) != 0
        try:
            return int(device_id) in self._devices_by_id
        except (ValueError, TypeError):
            return False

    def get_device_id(self, name: str) -> int:
        return self._device_name_to_id.get(name, 0)

    def get_device_name(self, device_id: int) -> str:
        if device_id not in self._devices_by_id:
            self._raise_index_error(f"Invalid device ID: {device_id}")
        return str(self._devices_by_id[device_id]["Name"])

    def get_device_online(self, device_id: int) -> bool:
        if device_id not in self._devices_by_id:
            self._raise_index_error(f"Invalid device ID: {device_id}")
        return bool(self._devices_by_id[device_id].get("Online", False))

    def get_device_expect_offline(self, device_id: int) -> bool:
        if device_id not in self._devices_by_id:
            self._raise_index_error(f"Invalid device ID: {device_id}")
        return bool(self._devices_by_id[device_id].get("ExpectOffline", False))

    def get_device_temperature(self, device_id: int) -> float | None:
        if device_id not in self._devices_by_id:
            self._raise_index_error(f"Invalid device ID: {device_id}")
        val = self._devices_by_id[device_id].get("Temperature")
        if val is None:
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    def all_devices_online(self) -> bool:
        return all(dev.get("Online", False) for dev in self._devices_by_id.values())

    def get_json_snapshot(self) -> dict[str, Any]:
        return {
            "devices": self.snapshot.devices,
            "outputs": self.snapshot.outputs,
            "inputs": self.snapshot.inputs,
            "meters": self.snapshot.meters,
            "temp_probes": self.snapshot.temp_probes,
        }

    # ── Output lookups ──────────────────────────────────────────────────────

    def get_output_id(self, name: str) -> int:
        return self._output_name_to_id.get(name, 0)

    def validate_output_id(self, output_id: int | str) -> bool:
        if isinstance(output_id, str):
            return self.get_output_id(output_id) != 0
        try:
            return int(output_id) in self._outputs_by_id
        except (ValueError, TypeError):
            return False

    def get_output_state(self, output_id: int) -> bool:
        if output_id not in self._outputs_by_id:
            self._raise_index_error(f"Invalid output ID: {output_id}")
        device_id = self.get_output_device_id(output_id)
        if not self.get_device_online(device_id):
            return False
        return bool(self._outputs_by_id[output_id].get("State", False))

    def get_output_device_id(self, output_id: int) -> int:
        if output_id not in self._outputs_by_id:
            self._raise_index_error(f"Invalid output ID: {output_id}")
        return int(self._outputs_by_id[output_id].get("DeviceID", 0))

    # ── Input lookups ───────────────────────────────────────────────────────

    def get_input_id(self, name: str) -> int:
        return self._input_name_to_id.get(name, 0)

    def get_input_state(self, input_id: int) -> bool:
        if input_id not in self._inputs_by_id:
            self._raise_index_error(f"Invalid input ID: {input_id}")
        return bool(self._inputs_by_id[input_id].get("State", False))

    # ── Meter lookups ───────────────────────────────────────────────────────

    def get_meter_id(self, name: str) -> int:
        return self._meter_name_to_id.get(name, 0)

    def get_meter_energy(self, meter_id: int) -> float:
        if meter_id not in self._meters_by_id:
            self._raise_index_error(f"Invalid meter ID: {meter_id}")
        val = self._meters_by_id[meter_id].get("Energy", 0) or 0
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    def get_meter_power(self, meter_id: int) -> float:
        if meter_id not in self._meters_by_id:
            self._raise_index_error(f"Invalid meter ID: {meter_id}")
        val = self._meters_by_id[meter_id].get("Power", 0) or 0
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    # ── Temp probe lookups ──────────────────────────────────────────────────

    def get_temp_probe_id(self, name: str) -> int:
        return self._temp_probe_name_to_id.get(name, 0)

    def get_temp_probe_temperature(self, temp_probe_id: int) -> float | None:
        if temp_probe_id not in self._temp_probes_by_id:
            self._raise_index_error(f"Invalid temperature probe ID: {temp_probe_id}")
        val = self._temp_probes_by_id[temp_probe_id].get("Temperature")
        if val is None:
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    def get_temp_probe_reading_time(self, temp_probe_id: int) -> dt.datetime | None:
        if temp_probe_id not in self._temp_probes_by_id:
            self._raise_index_error(f"Invalid temperature probe ID: {temp_probe_id}")
        return self._temp_probes_by_id[temp_probe_id].get("LastReadingTime")
