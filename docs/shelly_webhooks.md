# Shelly webhooks

SCSmartDevices supports webhooks for Shelly smart switches. When enabled, a webhook server is started to listen for webhook events posted by a Shelly device. 
For example, your application can be immediately notified when an input switch on a Shelly smart switch is turned on or off. 

The SupportedWebhooks attrbute of a device object lists the webhook events that each device supports (if any). See this page for documentation:
https://shelly-api-docs.shelly.cloud/gen2/ComponentsAndServices/Webhook#webhookcreate

To use webhooks you must:

1. Properly configure the [ShellyWebhooks section](example_config.md#shellywebhooks-key) of the SCSmartDevices configuration block.
2. Have your client app running on a system that accepts inbound http connections on the IP address and port configured in the ShellyWebhooks section.
3. Be using a Shelly device (typically Gen 3 or later) that supports wbhooks. 
4. Add the _Webhooks_ key to a device's input of output configuration so that webhook handlers are installed for that component. 

Here's an example application:

```python
  {%
    include "../examples/switch_webhooks.py"
  %}
```

## Tasmota devices

Tasmota ESP32 devices don't support webhooks, but they do support signalling to a client app via Matter (MQTT) events. This will be supported in a later version of this package.