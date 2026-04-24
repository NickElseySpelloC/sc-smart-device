# Example using Shelly Webhooks

Below is a example application that uses Shelly Webhooks 

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
    include "../../examples/switch_webhooks.py"
  %}
```