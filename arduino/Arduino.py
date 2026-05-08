import serial
import time

ARDUINO_PORT = "COM3"  # Change based on your setup
BAUD_RATE = 9600

def send_command(command):
    try:
        arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)

        time.sleep(2)

        print(f"Connected to Arduino on {ARDUINO_PORT}")

        arduino.write((command + '\n').encode())

        print(f"Sent command: {command}")

    except serial.SerialException:
        print("Failed to connect to Arduino")



