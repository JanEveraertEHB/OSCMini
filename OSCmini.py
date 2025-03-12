import network
import socket
import struct

class OSCmini:
    _sock = None
    _buffer_size = 1024

    @staticmethod
    def start(ssid, password, ip, port):
        """ Connects to Wi-Fi and starts listening for OSC messages. """
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)
        print("Connecting to Wi-Fi...")
        while not wlan.isconnected():
            sleep(1)
        print("Connected! IP:", wlan.ifconfig()[0])

        # Setup UDP server
        OSCmini._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        OSCmini._sock.bind((ip, int(port)))
        print(f"Listening for OSC on {ip}:{port}...")

    @staticmethod
    def getMessage():
        """ Receives and parses an OSC message. Returns (address, value). """
        if OSCmini._sock:
            data, addr = OSCmini._sock.recvfrom(OSCmini._buffer_size)
            return OSCmini._parse_osc(data)
        return None

    @staticmethod
    def _parse_osc(data):
        """ Parses OSC messages including bundles and multiple arguments. """
        try:
            if data.startswith(b"#bundle"):
                # Skip "#bundle" and timestamp (8 bytes), then parse each message
                data = data[16:]
                messages = []
                while len(data) > 0:
                    size = struct.unpack(">I", data[:4])[0]  # Get message size
                    msg_data = data[4:4 + size]  # Extract message data
                    messages.append(OSCmini._parse_osc(msg_data))
                    data = data[4 + size:]  # Move to the next message
                return messages  # Return a list of parsed messages
            
            # Find the address string
            end = data.find(b"\x00")
            address = data[:end].decode()
            data = data[(end + 4) & ~3:]  # Align to 4 bytes
            
            # Find type tags (must start with ',')
            if data[0:1] != b"," or len(data) < 4:
                return address, None
            type_tags = data[1:data.find(b"\x00")].decode()
            data = data[(len(type_tags) + 2 + 3) & ~3:]  # Align to 4 bytes

            values = []
            for tag in type_tags:
                if tag == "f" and len(data) >= 4:
                    value = struct.unpack(">f", data[:4])[0]
                    values.append(round(value, 2))
                    data = data[4:]  # Move to next value

            return address, values if len(values) > 1 else values[0]  # Return single float if only one
        except Exception as e:
            print("OSC Parsing Error:", e)
            return None


