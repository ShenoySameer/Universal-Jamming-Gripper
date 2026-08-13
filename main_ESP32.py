import sys
import select
import time
from machine import I2C, Pin

# RELAY SETUP
pump_relay = Pin(26, Pin.OUT)
valve_relay = Pin(27, Pin.OUT)
pump_relay.value(0)
valve_relay.value(0)

# PCA9685 SETUP
# 1. Connect to the PCA9685 over I2C
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
address = 0x40

# 2. Configure the PCA9685 hardware to 50Hz
i2c.writeto_mem(address, 0x00, b'\x10')
time.sleep_ms(5)
i2c.writeto_mem(address, 0xFE, b'\x79')
i2c.writeto_mem(address, 0x00, b'\xa1')
time.sleep_ms(5)

# 3. Helper function to move the servo
def move_servo(channel, tick_value):
    register = 0x06 + (channel * 4)
    data = bytearray([0, 0, tick_value & 0xFF, tick_value >> 8])
    i2c.writeto_mem(address, register, data)

# 4. Set up a non-blocking listener for the USB cable
poll_obj = select.poll()
poll_obj.register(sys.stdin, select.POLLIN)
buffer = ""

while True:
    # Check if PyCharm has sent text down the USB cable
    poll_results = poll_obj.poll(0)
    if poll_results:
        # Read exactly one character at a time
        char = sys.stdin.read(1)

        # When PyCharm sends a newline ('\n'), the command is complete
        if char == '\n':
            try:
                # Check for pump or valve commands
                if buffer.startswith("PUMP"):
                    parts = buffer.split(',')
                    state = int(parts[1])
                    pump_relay.value(state)
                    print(f"Pump set to {state}")
                elif buffer.startswith("VALVE"):
                    parts = buffer.split(',')
                    state = int(parts[1])
                    valve_relay.value(state)
                    print(f"Valve set to {state}")
                else:
                    # Otherwise, treat it as a servo command
                    parts = buffer.split(',')
                    if len(parts) == 2:
                        channel = int(parts[0])
                        position = int(parts[1])
                        move_servo(channel, position)
            except Exception as e:
                print(f"Error processing command: {e}")

            # Clear the buffer for the next incoming command
            buffer = ""
        else:
            buffer += char

    # Delay to prevent the ESP32 from freezing
    time.sleep(0.01)