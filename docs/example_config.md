# Example Configuration File 

Below is an example YAML configuration, as used by the code examples available at /examples.

```yaml
  {%
    include "../examples/switch_config.yaml"
  %}
```

## Configuration Reference

The following SCSmartDevices: keys are supported:

| Parameter | Description | 
|:--|:--|
| AllowDebugLogging | Set to true to enable debug logging output | 
| ResponseTimeout | How long to wait (in seconds) before timeing out when making an API call or ping. | 
| RetryCount | How many retries to make if an API call times out. | 
| RetryDelay | How long to wait (in seconds) between retry attempts. | 
| PingAllowed | Set to False if ICMP isn't suppported by the route to your devices. |
| SimulationFileFolder | The folder to save JSON simulation files in. | 
| ShellyWebhooks | This optional section configures the webhooks to be installed on Shelly devices (not applicable to Tasmota devices) - see below.  | 
| Devices | A list of dicts, each on defining an individual device. - see below |

### ShellyWebhooks key

The ShellyWebhooks key in the configuration block supports the following keys :

| Parameter | Description | 
|:--|:--|
| Enabled | Enable or disable the webhook listener |
| Host | IP to listen for webhooks on. This should be the IP address of the machine running the app. Defaults to 0.0.0.0. |
| Port | Port to listen for webhooks on. Defaults to 8787. |
| Path | The URI path that webhooks will post to. |
| DefaultWebhooks | The webhooks to install by default. See the example above for format. Look at the SupportedWebhooks key of an initialised Shelly device to see which webhook events your device supports. Use the  get_device() call to get a device object.  |

> Please see the [Shelly Webhooks page](shelly_webhooks.md) for more information.

### Devices key

The Devices key in the configuration block supports the following keys:

| Parameter | Description | 
|:--|:--|
| Name | Your name for this device  |
| Model | Either the Shelly model ID for this device (if a Shelly device - see [Shelly Models List](shelly_models_list.md)) or "Tasmota" if this is a Tasmota ESP32 device. |
| Hostname | The network IP address or hostname for this device. |
| ID | Your numeric ID for this device. |
| Simulate | Set this to True if you don't have access to the device but still want to test your code. When True, this device will be in 'simulation' mode. Rather than make API calls to the device, the state will be written to and read from a local json file (with the same name as your Name entry). You can modify some of the values in this file to test your code. |
| ExpectOffline | If set to True, we can expect this device to be offline at times. No warnings will be issued when this happens |
| Inputs | A list of dicts defining the inputs (if any) for this device. This section is optional but if defined, the number of entries must match the number of inputs supported by this model. For each input, define a Name and/or an ID. <br><br>Optionally, add a **Webhooks**: True entry here to install the default webhooks on this input. |
| Outputs | A list of dicts defining the outputs (if any) for this device. This section is optional but if defined, the number of entries must match the number of outputs supported by this model. For each output, define a Name and/or an ID. <br><br>Optionally, add a **Webhooks**: True entry here to install the default webhooks on this input. |
| Meters | A list of dicts defining the meters (if any) for this device. Note that depending on the devices, the actual meters might be part of the output or seperate energy meters (EM1 API calls). Either way, in this class meters are reported seperately from outputs. This section is optional but if defined, the number of entries must match the number of meters supported by this model. For each meter, define a Name and/or an ID.<br><br>  Optionally, use the **MockRate** key to set a Watts / second metering rate for this meter when the device is in Simulation mode. |
| TempProbes | A list of dicts defining the temperature probes connected to a Shelly Add-on that's plugged into this device. For each one you must define a Name key that matches the name given to the probe in the app (see below).<br><br>  Optionally, use the **RequiresOutput** key to specify the name of an output device that constrains this temp probe. If set, the temperature reading will only be updated when this output is on.  |

Notes:

- Either a Device Name or a Device ID must be supplied.

## Shelly device components

Shelly hardware devices can potentially have a combination of four types of component - inputs, outputs, meters and temp. probes. These are configured under the Devices: key of the SCSmartDevices: configuration. If you specify an ID and/or name for a device's component (e.g. the two output components of a Shelly2PMG3), then you must define _all_ the components of this type for that device. If the number of configured components don't match the number of actual components of that type (as defined in the models library), then the SCSmartDevices() initialisation will fail.

If you leave the configuration blank for a device's components, then the system will create default IDs and names for you.

## Tasmota device components

Due to the very large range of Tasmota devices on the market, it's not possible to maintain a library reference of each model and the type & number of components each model supports. 

Therefore, you **must** configure each componenet in your YAML configuration as this will dictate the capabilities of the device.

## Custom Attrbutes 

You can add custom key/values to Devices, Inputs, Outputs and Meters if needed. For example you could add a Group name to each output switch:

```yaml
SCSmartDevices:
  ...
  Devices:
    - Name: Downstairs Lights
      Model: Shelly2PMG3
      Hostname: 192.168.1.23
      ID: 100
      Inputs:
        - Name: "Living Room Switch"
          Webhooks: True
        - Name: "Kitchen Switch"
          Webhooks: True
      Outputs:
        - Name: "Living Room Relay"
          Group: Inside
        - Name: "Kitchen Relay"
          Group: Inside
    - Name: Outside Lights
      Model: Shelly2PMG3
      Hostname: 192.168.1.25
      ID: 200
      Inputs:
        - Name: "Patio Switch"
          Group: Outside
        - Name: "Car Port Switch"
          Group: Outside
      Outputs:
        - Name: "Patio Relay"
        - Name: "Car Port Relay"
    - Name: Testing
      ...
```

If you add custom attributes, you will need to include them in yoour Ceribus validation dict passed to SCConfigManager(). This will be merged in with the default validation structure:

```python
    "SCSmartDevices": {
        "schema": {
            "Devices": {
                "schema": {
                    "schema": {
                        "Outputs": {
                            "schema": {
                                "schema": {
                                    "Group": {"type": "string", "required": False, "nullable": True},
                                },
                            },
                        },
                    },
                },
            },
        }
    }
```


These custom attrbutes will be printed by the print_device_status() function and available from the get_**() functions.