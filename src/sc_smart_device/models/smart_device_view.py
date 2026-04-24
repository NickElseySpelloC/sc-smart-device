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

    # ── Generic value getter (standard + custom keys) ──────────────────────

    def _get_value(
        self,
        index: dict[int, dict[str, Any]],
        item_id: int,
        key_name: str,
        default: Any,
        id_label: str,
    ) -> Any:
        """Shared implementation for all get_X_value() methods.

        Returns:
            The value for ``key_name`` from the indexed item, or ``default``.
        """
        if item_id not in index:
            self._raise_index_error(f"Invalid {id_label} ID: {item_id}")
        return index[item_id].get(key_name, default)

    # ── Device lookups ──────────────────────────────────────────────────────

    def get_device_id_list(self) -> list[int]:
        """Return a list of all device IDs.

        Returns:
            List of integer device IDs for all configured devices.
        """
        return list(self._devices_by_id.keys())

    def validate_device_id(self, device_id: int | str) -> bool:
        """Check whether a device ID or name refers to a known device.

        Args:
            device_id: Integer device ID or device name string.

        Returns:
            True if the device exists, False otherwise.
        """
        if isinstance(device_id, str):
            return self.get_device_id(device_id) != 0
        try:
            return int(device_id) in self._devices_by_id
        except (ValueError, TypeError):
            return False

    def get_device_id(self, name: str) -> int:
        """Return the device ID for the given device name.

        Args:
            name: The device name to look up.

        Returns:
            The integer device ID, or 0 if not found.
        """
        return self._device_name_to_id.get(name, 0)

    def get_device_name(self, device_id: int) -> str:
        """Return the name of the device with the given ID.

        Args:
            device_id: The integer device ID.

        Returns:
            The device name string.

        Raises:
            IndexError: If the device ID is not found.
        """  # noqa: DOC502
        if device_id not in self._devices_by_id:
            self._raise_index_error(f"Invalid device ID: {device_id}")
        return str(self._devices_by_id[device_id]["Name"])

    def get_device_online(self, device_id: int) -> bool:
        """Return whether the device is currently online.

        Args:
            device_id: The integer device ID.

        Returns:
            True if the device is online, False otherwise.

        Raises:
            IndexError: If the device ID is not found.
        """  # noqa: DOC502
        if device_id not in self._devices_by_id:
            self._raise_index_error(f"Invalid device ID: {device_id}")
        return bool(self._devices_by_id[device_id].get("Online", False))

    def get_device_expect_offline(self, device_id: int) -> bool:
        """Return whether the device is configured to be expected offline.

        Args:
            device_id: The integer device ID.

        Returns:
            True if the device is expected to be offline, False otherwise.

        Raises:
            IndexError: If the device ID is not found.
        """  # noqa: DOC502
        if device_id not in self._devices_by_id:
            self._raise_index_error(f"Invalid device ID: {device_id}")
        return bool(self._devices_by_id[device_id].get("ExpectOffline", False))

    def get_device_temperature(self, device_id: int) -> float | None:
        """Return the current temperature of the device, if available.

        Args:
            device_id: The integer device ID.

        Returns:
            Temperature in degrees Celsius as a float, or None if unavailable.

        Raises:
            IndexError: If the device ID is not found.
        """  # noqa: DOC502
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
        """Return True if every configured device is currently online.

        Returns:
            True if all devices are online, False if any device is offline.
        """
        return all(dev.get("Online", False) for dev in self._devices_by_id.values())

    def get_device_value(self, device_id: int, key_name: str, default: Any = None) -> Any:
        """Return any attribute from a device's normalized snapshot dict.

        Use this for standard fields not covered by a dedicated getter (e.g.
        ``"MacAddress"``, ``"Uptime"``) and for custom keys defined in the
        app's YAML config.

        Args:
            device_id: The integer device ID.
            key_name: The dict key to retrieve.
            default: Value returned when the key is absent. Defaults to None.

        Returns:
            The value for ``key_name``, or ``default`` if the key is not present.

        Raises:
            IndexError: If the device ID is not found.
        """  # noqa: DOC502
        return self._get_value(self._devices_by_id, device_id, key_name, default, "device")

    def get_json_snapshot(self) -> dict[str, Any]:
        """Return a plain-dict snapshot of all component lists.

        Returns:
            Dict with keys ``devices``, ``outputs``, ``inputs``, ``meters``,
            and ``temp_probes``, each containing the corresponding list.
        """
        return {
            "devices": self.snapshot.devices,
            "outputs": self.snapshot.outputs,
            "inputs": self.snapshot.inputs,
            "meters": self.snapshot.meters,
            "temp_probes": self.snapshot.temp_probes,
        }

    # ── Output lookups ──────────────────────────────────────────────────────

    def get_output_id(self, name: str) -> int:
        """Return the output ID for the given output name.

        Args:
            name: The output name to look up.

        Returns:
            The integer output ID, or 0 if not found.
        """
        return self._output_name_to_id.get(name, 0)

    def validate_output_id(self, output_id: int | str) -> bool:
        """Check whether an output ID or name refers to a known output.

        Args:
            output_id: Integer output ID or output name string.

        Returns:
            True if the output exists, False otherwise.
        """
        if isinstance(output_id, str):
            return self.get_output_id(output_id) != 0
        try:
            return int(output_id) in self._outputs_by_id
        except (ValueError, TypeError):
            return False

    def get_output_state(self, output_id: int) -> bool:
        """Return the current on/off state of the output.

        Returns False if the parent device is offline.

        Args:
            output_id: The integer output ID.

        Returns:
            True if the output is on, False if off or device is offline.

        Raises:
            IndexError: If the output ID is not found.
        """  # noqa: DOC502
        if output_id not in self._outputs_by_id:
            self._raise_index_error(f"Invalid output ID: {output_id}")
        device_id = self.get_output_device_id(output_id)
        if not self.get_device_online(device_id):
            return False
        return bool(self._outputs_by_id[output_id].get("State", False))

    def get_output_device_id(self, output_id: int) -> int:
        """Return the device ID that owns the given output.

        Args:
            output_id: The integer output ID.

        Returns:
            The integer device ID that owns this output.

        Raises:
            IndexError: If the output ID is not found.
        """  # noqa: DOC502
        if output_id not in self._outputs_by_id:
            self._raise_index_error(f"Invalid output ID: {output_id}")
        return int(self._outputs_by_id[output_id].get("DeviceID", 0))

    def get_output_value(self, output_id: int, key_name: str, default: Any = None) -> Any:
        """Return any attribute from an output's normalized snapshot dict.

        Use this for standard fields not covered by a dedicated getter (e.g.
        ``"Temperature"``) and for custom keys defined in the app's YAML config
        (e.g. ``"Group"``).

        Args:
            output_id: The integer output ID.
            key_name: The dict key to retrieve.
            default: Value returned when the key is absent. Defaults to None.

        Returns:
            The value for ``key_name``, or ``default`` if the key is not present.

        Raises:
            IndexError: If the output ID is not found.
        """  # noqa: DOC502
        return self._get_value(self._outputs_by_id, output_id, key_name, default, "output")

    # ── Input lookups ───────────────────────────────────────────────────────

    def get_input_id(self, name: str) -> int:
        """Return the input ID for the given input name.

        Args:
            name: The input name to look up.

        Returns:
            The integer input ID, or 0 if not found.
        """
        return self._input_name_to_id.get(name, 0)

    def get_input_state(self, input_id: int) -> bool:
        """Return the current state of the input.

        Args:
            input_id: The integer input ID.

        Returns:
            True if the input is active, False otherwise.

        Raises:
            IndexError: If the input ID is not found.
        """  # noqa: DOC502
        if input_id not in self._inputs_by_id:
            self._raise_index_error(f"Invalid input ID: {input_id}")
        return bool(self._inputs_by_id[input_id].get("State", False))

    def get_input_value(self, input_id: int, key_name: str, default: Any = None) -> Any:
        """Return any attribute from an input's normalized snapshot dict.

        Use this for custom keys defined in the app's YAML config.

        Args:
            input_id: The integer input ID.
            key_name: The dict key to retrieve.
            default: Value returned when the key is absent. Defaults to None.

        Returns:
            The value for ``key_name``, or ``default`` if the key is not present.

        Raises:
            IndexError: If the input ID is not found.
        """  # noqa: DOC502
        return self._get_value(self._inputs_by_id, input_id, key_name, default, "input")

    # ── Meter lookups ───────────────────────────────────────────────────────

    def get_meter_id(self, name: str) -> int:
        """Return the meter ID for the given meter name.

        Args:
            name: The meter name to look up.

        Returns:
            The integer meter ID, or 0 if not found.
        """
        return self._meter_name_to_id.get(name, 0)

    def get_meter_energy(self, meter_id: int) -> float:
        """Return the cumulative energy reading from the meter.

        Args:
            meter_id: The integer meter ID.

        Returns:
            Energy in watt-hours as a float, or 0.0 if unavailable.

        Raises:
            IndexError: If the meter ID is not found.
        """  # noqa: DOC502
        if meter_id not in self._meters_by_id:
            self._raise_index_error(f"Invalid meter ID: {meter_id}")
        val = self._meters_by_id[meter_id].get("Energy", 0) or 0
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    def get_meter_power(self, meter_id: int) -> float:
        """Return the current power reading from the meter.

        Args:
            meter_id: The integer meter ID.

        Returns:
            Power in watts as a float, or 0.0 if unavailable.

        Raises:
            IndexError: If the meter ID is not found.
        """  # noqa: DOC502
        if meter_id not in self._meters_by_id:
            self._raise_index_error(f"Invalid meter ID: {meter_id}")
        val = self._meters_by_id[meter_id].get("Power", 0) or 0
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    def get_meter_value(self, meter_id: int, key_name: str, default: Any = None) -> Any:
        """Return any attribute from a meter's normalized snapshot dict.

        Use this for standard fields not covered by a dedicated getter (e.g.
        ``"Voltage"``, ``"Current"``, ``"PowerFactor"``) and for custom keys.

        Args:
            meter_id: The integer meter ID.
            key_name: The dict key to retrieve.
            default: Value returned when the key is absent. Defaults to None.

        Returns:
            The value for ``key_name``, or ``default`` if the key is not present.

        Raises:
            IndexError: If the meter ID is not found.
        """  # noqa: DOC502
        return self._get_value(self._meters_by_id, meter_id, key_name, default, "meter")

    # ── Temp probe lookups ──────────────────────────────────────────────────

    def get_temp_probe_id(self, name: str) -> int:
        """Return the temperature probe ID for the given probe name.

        Args:
            name: The temperature probe name to look up.

        Returns:
            The integer temperature probe ID, or 0 if not found.
        """
        return self._temp_probe_name_to_id.get(name, 0)

    def get_temp_probe_temperature(self, temp_probe_id: int) -> float | None:
        """Return the most recent temperature reading from the probe.

        Args:
            temp_probe_id: The integer temperature probe ID.

        Returns:
            Temperature in degrees Celsius as a float, or None if unavailable.

        Raises:
            IndexError: If the temperature probe ID is not found.
        """  # noqa: DOC502
        if temp_probe_id not in self._temp_probes_by_id:
            self._raise_index_error(f"Invalid temperature probe ID: {temp_probe_id}")
        val = self._temp_probes_by_id[temp_probe_id].get("Temperature")
        if val is None:
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    def get_temp_probe_value(self, temp_probe_id: int, key_name: str, default: Any = None) -> Any:
        """Return any attribute from a temperature probe's normalized snapshot dict.

        Use this for custom keys defined in the app's YAML config.

        Args:
            temp_probe_id: The integer temperature probe ID.
            key_name: The dict key to retrieve.
            default: Value returned when the key is absent. Defaults to None.

        Returns:
            The value for ``key_name``, or ``default`` if the key is not present.

        Raises:
            IndexError: If the temperature probe ID is not found.
        """  # noqa: DOC502
        return self._get_value(self._temp_probes_by_id, temp_probe_id, key_name, default, "temp_probe")

    def get_temp_probe_reading_time(self, temp_probe_id: int) -> dt.datetime | None:
        """Return the datetime of the last reading from the temperature probe.

        Args:
            temp_probe_id: The integer temperature probe ID.

        Returns:
            A ``datetime`` object for the last reading time, or None if no
            reading has been recorded yet.

        Raises:
            IndexError: If the temperature probe ID is not found.
        """  # noqa: DOC502
        if temp_probe_id not in self._temp_probes_by_id:
            self._raise_index_error(f"Invalid temperature probe ID: {temp_probe_id}")
        return self._temp_probes_by_id[temp_probe_id].get("LastReadingTime")
