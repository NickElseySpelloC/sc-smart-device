# Example reading temperature probes

Below is a example application that reads internal and external termperature sensors.

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
    include "../../examples/switch_temperature.py"
  %}
```