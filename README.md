# OSCMini
Small micropython script to add to your RP Pico W


# Usage
Add the OSCmini.py file to your RP pico device and add the following code in the main
```python
from OSCmini import OSCmini

# Start OSC listener with Wi-Fi credentials and port
OSCmini.start([SSID], [SSID_PWD], "255.255.255.255", 9000)

while True:
    message = OSCmini.getMessage()
    if message:
        if isinstance(message, list):  # If bundle, iterate over messages
            for msg in message:
                if msg:
                    address, value = msg
                    print(f"Received OSC: {address} -> {value}")
        else:
            address, value = message
            print(f"Received OSC: {address} -> {value}")

```
