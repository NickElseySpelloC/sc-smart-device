# Example using the SmartDeviceWorker class 

Example code using the [SmartDeviceWorker](../sc_smart_device_worker.md) class which implements a worker thread to 
manage the interface to a SCSmartDevice() instance. 

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
    include "../../examples/switch_worker.py"
  %}
```
