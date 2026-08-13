import serial
import time
import pygame

# Connect to the ESP32
COM_PORT = 'COM7'
BAUD_RATE = 115200

print(f"Connecting to ESP32 on {COM_PORT}...")
try:
    esp32 = serial.Serial(COM_PORT, BAUD_RATE, timeout=0.1)
    esp32.setDTR(False)
    esp32.setRTS(False)
    time.sleep(2)
    print("Connected successfully!")
except Exception as e:
    print(f"Failed to connect: {e}")
    exit()

# Robot Arm Configuration
SAFE_MIN = 50
SAFE_MAX = 450

# WIRING CONFIGURATION
CH_0 = 0
CH_A = 1
CH_E = 2
CH_4 = 4

# Starting Positions
ch0_pos = 303.0
chA_pos = 311.0
chE_pos = 290.0
ch4_pos = 250.0

# Speed multiplier
SPEED = 6.0

def send_command(channel, position):
    command_text = f"{channel},{int(position)}\n"
    esp32.write(command_text.encode('utf-8'))

def stop_and_release():
    """Turn pump off and open valve so the gripper vents back to room pressure."""
    esp32.write(b"PUMP,0\n")
    esp32.write(b"VALVE,1\n")
    time.sleep(0.1)

# Setup Pygame & USB Controller
pygame.init()
pygame.joystick.init()
screen = pygame.display.set_mode((300, 200))
pygame.display.set_caption("Direct Robot Commander")

if pygame.joystick.get_count() == 0:
    print("ERROR: No USB controller found! Please plug it in.")
    exit()

controller = pygame.joystick.Joystick(0)
controller.init()
print(f"Connected to Gamepad: {controller.get_name()}")
print("Left Stick L/R: Channel 0")
print("Left Stick U/D: Channel A")
print("Right Stick U/D: Channel E")
print("Press 'A'/'Cross' to GRAB, 'X'/'Square' to RELEASE")
print("Press 'B' or 'Circle' to quit (auto-releases first).")

# Wake up and center the robot
send_command(CH_0, ch0_pos)
send_command(CH_A, chA_pos)
send_command(CH_E, chE_pos)
send_command(CH_4, ch4_pos)
time.sleep(1)

# The Main Control Loop
running = True

old_ch0 = int(ch0_pos)
old_chA = int(chA_pos)
old_chE = int(chE_pos)
old_ch4 = int(ch4_pos)

while running:
    # Check ESP32 Serial
    while esp32.in_waiting:
        esp32_message = esp32.readline().decode('utf-8', errors='ignore').strip()
        if esp32_message:
            print(f"ESP32 says: {esp32_message}")

    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 1:  # 'B' or 'Circle' - Quit
                print("Quitting program... releasing and stopping pump first")
                stop_and_release()
                running = False

            elif event.button == 0:  # 'A' or 'Cross' - GRAB
                print("Command: GRAB (Pump ON, valve open)")
                esp32.write(b"PUMP,1\n")
                esp32.write(b"VALVE,1\n")

            elif event.button == 2:  # 'X' or 'Square' - RELEASE
                print("Command: RELEASE (Pump OFF, valve open to vent)")
                stop_and_release()

    # READ CONTROLLER INPUTS

    # 1. Channel 0: Left Stick Left/Right
    stick_lx = controller.get_axis(0)
    if abs(stick_lx) > 0.2:
        ch0_pos += stick_lx * SPEED

    # 2. Channel A: Left Stick Up/Down
    stick_ly = controller.get_axis(1)
    if abs(stick_ly) > 0.2:
        chA_pos += stick_ly * SPEED

    # 3. Channel E: Right Stick Up/Down
    stick_ry = controller.get_axis(3)
    if abs(stick_ry) > 0.2:
        chE_pos -= stick_ry * SPEED

    # APPLY SAFETY CLAMPS
    ch0_pos = max(SAFE_MIN, min(SAFE_MAX, ch0_pos))
    chA_pos = max(SAFE_MIN, min(SAFE_MAX, chA_pos))
    chE_pos = max(SAFE_MIN, min(SAFE_MAX, chE_pos))
    ch4_pos = max(SAFE_MIN, min(SAFE_MAX, ch4_pos))

    # SEND COMMANDS IF MOVED
    cur_ch0 = int(ch0_pos)
    cur_chA = int(chA_pos)
    cur_chE = int(chE_pos)
    cur_ch4 = int(ch4_pos)

    if cur_ch0 != old_ch0:
        send_command(CH_0, cur_ch0)
        old_ch0 = cur_ch0

    if cur_chA != old_chA:
        send_command(CH_A, cur_chA)
        old_chA = cur_chA

    if cur_chE != old_chE:
        send_command(CH_E, cur_chE)
        old_chE = cur_chE

    if cur_ch4 != old_ch4:
        send_command(CH_4, cur_ch4)
        old_ch4 = cur_ch4

    time.sleep(0.08)

stop_and_release()
esp32.close()
pygame.quit()
print("Connection closed.")
