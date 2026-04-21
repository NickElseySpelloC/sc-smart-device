from __future__ import annotations

from abc import ABC, abstractmethod

from sc_smart_device.models.smart_device_status import SmartDeviceStatus


class BaseProvider(ABC):
    """Abstract base class that every hardware provider must implement.

    SCSmartDevice owns one or more providers and calls this contract to:
    - load device configuration
    - refresh device state
    - control outputs
    - start/stop provider-specific background services (e.g. webhook server)
    - produce a normalized SmartDeviceStatus snapshot
    """

    @abstractmethod
    def initialize_settings(self, provider_config: dict, refresh_status: bool = True) -> None:
        """Load provider config, build internal device list, optionally refresh state."""

    @abstractmethod
    def get_device_status(self, device_identity: dict | int | str) -> bool:
        """Refresh one device's state. Returns True if online, False if offline."""

    @abstractmethod
    def refresh_all_device_statuses(self) -> None:
        """Refresh state for every device owned by this provider."""

    @abstractmethod
    def set_output(self, output_identity: dict | int | str, new_state: bool) -> tuple[bool, bool]:
        """Set an output state. Returns (success, did_change)."""

    @abstractmethod
    def get_device_location(self, device_identity: dict | int | str) -> dict | None:
        """Return timezone / lat / lon dict for device, or None."""

    @abstractmethod
    def start_services(self) -> None:
        """Start any background services (e.g. webhook HTTP server)."""

    @abstractmethod
    def stop_services(self) -> None:
        """Stop background services and release resources."""

    @abstractmethod
    def get_normalized_status(self) -> SmartDeviceStatus:
        """Return a normalized snapshot with provider-agnostic public dicts."""
