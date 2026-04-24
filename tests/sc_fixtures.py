"""Shared test fixtures for sc-smart-device test suite.

Import this module in each test file::

    from test_setup import config, logger, smart_device
    from test_setup import DEVICE_CLIENTNAME, DEVICE_ID, OUTPUT_1_NAME, ...

This module is cached after the first import, so setup runs only once regardless
of how many test files import it.
"""

import sys

from mergedeep import merge
from sc_foundation import SCConfigManager, SCLogger

from examples.validation_extras import smart_switch_extra_validation
from sc_smart_device import SCSmartDevice, smart_devices_validator

# ── Config ───────────────────────────────────────────────────────────────────

CONFIG_FILE = "tests/config.yaml"

# ── Well-known device / component identifiers ─────────────────────────────────
# Shelly device (Device Test 1)
DEVICE_CLIENTNAME = "Device Test 1"
DEVICE_ID = 1           # Auto-assigned (first device, no explicit ID in config)
OUTPUT_1_NAME = "Device 1.Output 1"
OUTPUT_2_NAME = "Device 1.Output 2"
INPUT_1_NAME = "Device 1.Input 1"
INPUT_2_NAME = "Device 1.Input 2"
METER_1_NAME = "Meter 1"    # Auto-generated (no Meters: block in config)
METER_2_NAME = "Meter 2"

# Tasmota device (Device Test 2)
TASMOTA_DEVICE_NAME = "Device Test 2"
TASMOTA_DEVICE_ID = 2
TASMOTA_OUTPUT_NAME = "Device 2.Output 1"
TASMOTA_OUTPUT_ID = 3   # Auto-assigned: Shelly outputs claim IDs 1 & 2
TASMOTA_METER_NAME = "Device 2.Meter 1"
TASMOTA_METER_ID = 3    # Auto-assigned: Shelly meters claim IDs 1 & 2

# ── Initialisation ───────────────────────────────────────────────────────────

print("Initialising sc-smart-device test fixtures...")

# Merge the SmartDevices validation schema with the app-level extras
merged_schema = merge({}, smart_devices_validator, smart_switch_extra_validation)
assert isinstance(merged_schema, dict), "Merged schema should be type dict"

try:
    config = SCConfigManager(
        config_file=CONFIG_FILE,
        validation_schema=merged_schema,
    )
except RuntimeError as e:
    print(f"Configuration file error: {e}", file=sys.stderr)
    sys.exit(1)

assert config is not None, "ConfigManager should be initialized"

try:
    logger = SCLogger(config.get_logger_settings())
except RuntimeError as e:
    print(f"Logger initialisation error: {e}", file=sys.stderr)
    sys.exit(1)

assert logger is not None, "Logger should be initialized"

smart_switch_settings = config.get("SCSmartDevices")
assert smart_switch_settings is not None, "SCSmartDevice settings should be present in config"

try:
    smart_device = SCSmartDevice(logger, smart_switch_settings)  # type: ignore[call-arg]
except RuntimeError as e:
    print(f"SCSmartDevice initialization error: {e}", file=sys.stderr)
    sys.exit(1)

assert smart_device is not None, "SCSmartDevice should be initialized"
