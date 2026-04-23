"""Extensions to the SCSmartSwitch configuration validation."""


smart_switch_extra_validation = {
    "SCSmartDevices": {
        "schema": {
            "Devices": {
                "schema": {
                    "schema": {
                        "Outputs": {
                            "schema": {
                                "schema": {
                                    "Colour": {"type": "string", "required": False, "nullable": True},
                                    "Group": {"type": "string", "required": False, "nullable": True},
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
