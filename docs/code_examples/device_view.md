# Example using the SmartDeviceView

Below is a example application using the [SmartDeviceView](../sc_smart_device_view.md) class. This class provides a read-only, 
thread safe copy of the device and component status information. It's typically used in conjunction
with the [SmartDeviceWorker](device_worker.md) class.


## Module to initialise the SCSmartDevice instance

See the [example config](../example_config.md) page for the YAML configuration used by this example.

```python
  {%
    include "../../examples/switch_init.py"
  %}
```

## Example application

```python
  {%
    include "../../examples/switch_basic.py"
  %}
```