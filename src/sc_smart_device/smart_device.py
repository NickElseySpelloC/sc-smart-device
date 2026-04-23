"""SCSmartDevice — the stable public API for controlling smart devices.

Client apps should only depend on this class, not on any provider directly.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sc_smart_device.models.smart_device_view import SmartDeviceView
from sc_smart_device.providers.shelly_provider import ShellyProvider

if TYPE_CHECKING:
    import threading

    from sc_foundation import SCLogger


class SCSmartDevice:  # noqa: PLR0904
    """Unified smart-device controller."""

    def __init__(
        self,
        logger: SCLogger,
        device_settings: dict,
        app_wake_event: threading.Event | None = None,
    ) -> None:
        """Accepts the ``SCSmartDevices:`` config block parsed from the client app's YAML file and instantiates the appropriate hardware providers.

        Signature matches the legacy ``ShellyControl`` constructor so existing
        client apps require minimal changes.

        Args:
            logger: SCLogger instance from sc-foundation.
            device_settings: The ``SCSmartDevices`` dict from the app config.
            app_wake_event: Optional threading.Event set when a webhook fires.

        Raises:
            RuntimeError: If config is invalid or the model file cannot be loaded.
        """  # noqa: DOC502
        self._logger = logger
        self._provider = ShellyProvider(logger, app_wake_event)
        self._provider.initialize_settings(device_settings)
        self._provider.start_services()

    # ── Re-initialise ────────────────────────────────────────────────────────

    def initialize_settings(self, device_settings: dict, refresh_status: bool = True) -> None:
        """Reload device configuration without restarting the webhook server.

        Useful for hot-reloading when the YAML config file changes at runtime.

        Args:
            device_settings: Updated ``SCSmartDevices`` dict.
            refresh_status: If True (default) refresh device state after loading.
        """
        self._provider.initialize_settings(device_settings, refresh_status)

    # ── Public list properties (normalized, provider-agnostic copies) ─────────

    @property
    def devices(self) -> list[dict]:
        """Normalized snapshot of all device dicts."""
        return self._provider.get_normalized_status().devices

    @property
    def inputs(self) -> list[dict]:
        """Normalized snapshot of all input component dicts."""
        return self._provider.get_normalized_status().inputs

    @property
    def outputs(self) -> list[dict]:
        """Normalized snapshot of all output component dicts."""
        return self._provider.get_normalized_status().outputs

    @property
    def meters(self) -> list[dict]:
        """Normalized snapshot of all meter component dicts."""
        return self._provider.get_normalized_status().meters

    @property
    def temp_probes(self) -> list[dict]:
        """Normalized snapshot of all temperature probe dicts."""
        return self._provider.get_normalized_status().temp_probes

    # ── Thread-safe view ────────────────────────────────────────────────────

    def get_view(self) -> SmartDeviceView:
        """Return a frozen, indexed, thread-safe snapshot of current device state.

        Use this in multi-threaded applications (e.g. alongside SmartDeviceWorker)
        to safely read device state without holding a lock.

        Returns:
            SmartDeviceView built from the current normalized status.
        """
        return SmartDeviceView(self._provider.get_normalized_status())

    # ── Live internal lookups (mutable dicts, all fields) ────────────────────
    # These return references into the provider's internal state so that the
    # existing pattern of "hold a reference, read State after refresh" continues
    # to work.  Provider-internal fields (Protocol, DeviceIndex, etc.) are
    # accessible here but not exposed through the normalized properties above.

    def get_device(self, device_identity: dict | int | str) -> dict:
        """Returns the device index for a given device ID or name.

        For device_identity you can pass:
        - A device object (dict) to retrieve it directly.
        - The device ID (int) to look it up by ID.
        - The device name (str) to look it up by name.
        - A component object (dict), which will return the parent device.

        Args:
            device_identity (dict | int | str): The identifier for the device.

        Returns:
            device (dict): The device object if found.

        Raises:
            RuntimeError: If the device is not found in the list of devices.
        """  # noqa: DOC502
        return self._provider.get_device(device_identity)

    def get_device_component(
        self,
        component_type: str,
        component_identity: int | str,
        use_index: bool | None = None,
    ) -> dict:
        """Returns a device component's index for a given component ID or name.

        Args:
            component_type (str): The type of component to retrieve ('input', 'output', 'meter' or 'temp_probe').
            component_identity (int | str): The ID or name of the component to retrieve.
            use_index (bool | None): If True, lookup by index instead of ID or name.

        Returns:
            component(dict): The component index if found.

        Raises:
            RuntimeError: If the component is not found in the list.
        """  # noqa: DOC502
        return self._provider.get_device_component(component_type, component_identity, use_index)

    # ── Convenience component shorthand ─────────────────────────────────────

    def get_output(self, output_identity: int | str) -> dict:
        """Shorthand for ``get_device_component("output", output_identity)``.

        Returns:
            The internal output component dict.
        """
        return self._provider.get_device_component("output", output_identity)

    def get_input(self, input_identity: int | str) -> dict:
        """Shorthand for ``get_device_component("input", input_identity)``.

        Returns:
            The internal input component dict.
        """
        return self._provider.get_device_component("input", input_identity)

    def get_meter(self, meter_identity: int | str) -> dict:
        """Shorthand for ``get_device_component("meter", meter_identity)``.

        Returns:
            The internal meter component dict.
        """
        return self._provider.get_device_component("meter", meter_identity)

    def get_temp_probe(self, probe_identity: int | str) -> dict:
        """Shorthand for ``get_device_component("temp_probe", probe_identity)``.

        Returns:
            The internal temperature probe component dict.
        """
        return self._provider.get_device_component("temp_probe", probe_identity)

    # ── Device status ────────────────────────────────────────────────────────

    def is_device_online(self, device_identity: dict | int | str | None = None) -> bool:
        """See if a device is alive by pinging it.

        Returns the result and updates the device's online status. If we are in simulation mode, always returns True.

        Args:
            device_identity (Optional (dict | int | str | None), optional): The actual device object, device component object,
                        device ID or device name of the device to check. If None, checks all device.

        Returns:
            result (bool): True if the device is online, False otherwise. If all devices are checked, returns True if all device are online.

        Raises:
            RuntimeError: If the device is not found in the list of devices.
        """  # noqa: DOC502
        return self._provider.is_device_online(device_identity)

    def get_device_status(self, device_identity: dict | int | str) -> bool:
        """Gets the status of a Shelly device.

        Args:
            device_identity (dict | int | str): A device dict, or the ID or name of the device to check.

        Returns:
            result (bool): True if the device is online, False otherwise.

        Raises:
            RuntimeError: If the device is not found in the list of devices or if there is an error getting the status.
            TimeoutError: If the device is online (ping) but the request times out while getting the device status.
        """  # noqa: DOC502
        return self._provider.get_device_status(device_identity)

    def refresh_all_device_statuses(self) -> None:
        """Refreshes the status of all Shelly devices.

        This function iterates through all devices and updates their status by calling get_device_status.
        It also calculates the total power and energy consumption for each device.

        Raises:
            RuntimeError: If there is an error getting the status of any device.
        """  # noqa: DOC502
        self._provider.refresh_all_device_statuses()

    def refresh(self) -> None:
        """Alias for :meth:`refresh_all_device_statuses`."""
        self._provider.refresh_all_device_statuses()

    # ── Output control ───────────────────────────────────────────────────────

    def change_output(
        self, output_identity: dict | int | str, new_state: bool
    ) -> tuple[bool, bool]:
        """Change an output relay to the requested state.

        Args:
            output_identity: Output dict, ID, or name.
            new_state: True to turn on, False to turn off.

        Returns:
            ``(success, did_change)`` — success is False when the device is
            offline; did_change is False when the output was already in the
            requested state.

        Raises:
            RuntimeError: There was an error changing the device output state.
            TimeoutError: If the device is online (ping) but the state change request times out.

        """  # noqa: DOC502
        return self._provider.set_output(output_identity, new_state)

    # ── Webhooks ─────────────────────────────────────────────────────────────

    def install_webhook(
        self,
        event: str,
        component: dict,
        url: str | None = None,
        additional_payload: dict | None = None,
    ) -> None:
        """Install a webhook on a device component.

        See https://nickelseyspelloc.github.io/sc-smart-device/shelly_webhooks/ for details on supported events and payloads.

        Args:
            event: Shelly event name, e.g. ``"input.toggle_on"``.
            component: Component dict (from :meth:`get_device_component`).
            url: Override the callback URL. Auto-constructed if None.
            additional_payload: Extra query-string parameters to include.
        """
        self._provider.install_webhook(event, component, url, additional_payload)

    def pull_webhook_event(self) -> dict | None:
        """Return the oldest queued webhook event and remove it from the queue.

        Use this if your app has been interrupted by a webhook event (your app_wake_event was set).
        This will return the earliest webhook event that was received and remove it from the queue.

        Returns:
            Event dict with keys ``timestamp``, ``Event``, ``Device``,
            ``Component``, etc.; or None if the queue is empty.
        """
        return self._provider.pull_webhook_event()

    def does_device_have_webhooks(self, device: dict) -> bool:
        """Return True if any component of the device has webhooks enabled."""
        return self._provider.does_device_have_webhooks(device)

    # ── Device location ──────────────────────────────────────────────────────

    def get_device_location(self, device_identity: dict | int | str) -> dict | None:
        """Gets the timezone and location of a Shelly device if available.

        Returns a dict in the following format:
           "tz": "Europe/Sofia",
           "lat": 42.67236,
           "lon": 23.38738

        Args:
            device_identity (dict | int | str): A device dict, or the ID or name of the device to check.

        Returns:
            location (dict | None): A dictionary containing the timezone and location of the device, or None if not available.

        Raises:
            RuntimeError: If the device is not found in the list of devices or if there is an error getting the status.
            TimeoutError: If the device is online (ping) but the request times out while getting the device status.
        """  # noqa: DOC502
        return self._provider.get_device_location(device_identity)

    # ── Device information ───────────────────────────────────────────────────

    def get_device_information(
        self, device_identity: dict | int | str, refresh_status: bool = False
    ) -> dict:
        """Return a consolidated copy of one device and all its components.

        Args:
            device_identity: Device dict, ID, or name.
            refresh_status: If True, fetch fresh state from hardware first.

        Returns:
            Device dict augmented with ``Inputs``, ``Outputs``, ``Meters``,
            and ``TempProbes`` sub-lists.

        Raises:
            RuntimeError: If the device is not found in the list of devices or if there is an error getting the status.
        """  # noqa: DOC502
        return self._provider.get_device_information(device_identity, refresh_status)

    # ── Diagnostics ──────────────────────────────────────────────────────────

    def print_device_status(self, device_identity: int | str | None = None) -> str:
        """Prints the status of a device or all devices.

        Args:
            device_identity (Optional (int | str | None), optional): The ID or name of the device to check. If None, checks all devices.

        Returns:
            device_info (str): A string representation of the device status.

        Raises:
            RuntimeError: If the device is not found in the list of devices.
        """  # noqa: DOC502
        return self._provider.print_device_status(device_identity)

    def print_model_library(self, mode_str: str = "brief", model_id: str | None = None) -> str:
        """Prints the Shelly model library.

        Args:
            mode_str (str, optional): The mode of printing. Can be "brief" or "detailed". Defaults to "brief".
            model_id (Optional (str), optional): If provided, filters the models by this model name. If None, prints all models.

        Returns:
            library_info (str): A string representation of the Shelly model library.
        """
        return self._provider.print_model_library(mode_str, model_id)

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def shutdown(self) -> None:
        """Stop the webhook server and release all resources.

        Call this when the client application is terminating.
        """
        self._provider.stop_services()
