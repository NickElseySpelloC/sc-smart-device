from enum import StrEnum


class DeviceCapability(StrEnum):
    OUTPUT_CONTROL = "output_control"
    OUTPUT_STATE = "output_state"
    INPUT_READ = "input_read"
    TEMPERATURE = "temperature"
    METERING = "metering"
    WEBHOOKS = "webhooks"
    SIMULATION = "simulation"
    POLLING = "polling"
    DEVICE_LOCATION = "device_location"
