"""Configuration schemas for use with the SCConfigManager class."""


class ConfigSchema:
    """Base class for configuration schemas."""

    def __init__(self):

        self.smart_switch_extra_validation = {
            "SCSmartDevices": {
                "schema": {
                    "Devices": {
                        "schema": {
                            "schema": {
                                "Outputs": {
                                    "schema": {
                                        "schema": {
                                            "Colour": {"type": "string", "required": False, "nullable": True},
                                            "Size": {"type": "string", "required": False, "nullable": True},
                                        },
                                    },
                                },
                            },
                        },
                    },
                }
            }
        }
