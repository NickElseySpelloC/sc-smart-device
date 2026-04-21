from dataclasses import dataclass


@dataclass
class SmartDeviceStatus:
    """Mutable snapshot of all device and component state across all providers."""
    devices: list[dict]
    outputs: list[dict]
    inputs: list[dict]
    meters: list[dict]
    temp_probes: list[dict]
