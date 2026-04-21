"""Cerberus validation schema fragment for the SCSmartDevices YAML config block.

Client apps should merge this into their own validation schema and pass the combined
schema to SCConfigManager so the full config file is validated in one pass.

Example::

    from sc_smart_device import smart_devices_validator
    from sc_foundation import SCConfigManager, yaml_config_validation

    merged_schema = {**yaml_config_validation, **smart_devices_validator}
    config = SCConfigManager(
        config_file="config.yaml",
        validation_schema=merged_schema,
    )
    device_settings = config.get("SCSmartDevices")
"""

_component_id_name = {
    "ID": {"type": "number", "required": False, "nullable": True},
    "Name": {"type": "string", "required": False, "nullable": True},
}

smart_devices_validator: dict = {
    "SCSmartDevices": {
        "type": "dict",
        "required": False,
        "nullable": True,
        "schema": {
            "AllowDebugLogging": {"type": "boolean", "required": False, "nullable": True},
            "ResponseTimeout": {
                "type": "number", "required": False, "nullable": True, "min": 1, "max": 120,
            },
            "RetryCount": {
                "type": "number", "required": False, "nullable": True, "min": 0, "max": 10,
            },
            "RetryDelay": {
                "type": "number", "required": False, "nullable": True, "min": 1, "max": 10,
            },
            "PingAllowed": {"type": "boolean", "required": False, "nullable": True},
            "SimulationFileFolder": {"type": "string", "required": False, "nullable": True},
            "ShellyWebhooks": {
                "type": "dict",
                "required": False,
                "nullable": True,
                "schema": {
                    "Enabled": {"type": "boolean", "required": False, "nullable": True},
                    "Host": {"type": "string", "required": False, "nullable": True},
                    "Port": {
                        "type": "number", "required": False, "nullable": True, "min": 1, "max": 65535,
                    },
                    "Path": {"type": "string", "required": False, "nullable": True},
                    "DefaultWebhooks": {
                        "type": "dict",
                        "required": False,
                        "nullable": True,
                        "schema": {
                            "Inputs": {
                                "type": "list", "required": False, "nullable": True,
                                "schema": {"type": "string"},
                            },
                            "Outputs": {
                                "type": "list", "required": False, "nullable": True,
                                "schema": {"type": "string"},
                            },
                            "Meters": {
                                "type": "list", "required": False, "nullable": True,
                                "schema": {"type": "string"},
                            },
                        },
                    },
                },
            },
            "Devices": {
                "type": "list",
                "required": True,
                "nullable": False,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "ID": {"type": "number", "required": False, "nullable": True},
                        "Name": {"type": "string", "required": False, "nullable": True},
                        "Model": {"type": "string", "required": True},
                        "Hostname": {"type": "string", "required": False, "nullable": True},
                        "Port": {"type": "number", "required": False, "nullable": True},
                        "Simulate": {"type": "boolean", "required": False, "nullable": True},
                        "ExpectOffline": {"type": "boolean", "required": False, "nullable": True},
                        "Inputs": {
                            "type": "list",
                            "required": False,
                            "nullable": True,
                            "schema": {
                                "type": "dict",
                                "schema": {
                                    **_component_id_name,
                                    "Webhooks": {"type": "boolean", "required": False, "nullable": True},
                                },
                            },
                        },
                        "Outputs": {
                            "type": "list",
                            "required": False,
                            "nullable": True,
                            "schema": {
                                "type": "dict",
                                "schema": {
                                    **_component_id_name,
                                    "Webhooks": {"type": "boolean", "required": False, "nullable": True},
                                },
                            },
                        },
                        "Meters": {
                            "type": "list",
                            "required": False,
                            "nullable": True,
                            "schema": {
                                "type": "dict",
                                "schema": {
                                    **_component_id_name,
                                    "MockRate": {"type": "number", "required": False, "nullable": True},
                                },
                            },
                        },
                        "TempProbes": {
                            "type": "list",
                            "required": False,
                            "nullable": True,
                            "schema": {
                                "type": "dict",
                                "schema": {
                                    **_component_id_name,
                                    "RequiresOutput": {"type": "string", "required": False, "nullable": True},
                                },
                            },
                        },
                    },
                },
            },
        },
    }
}
