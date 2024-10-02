import machine
from machine import Pin, PWM
from time import sleep
import time
import network
import socket

# Initialize network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('ITEK 1st', 'iteke23a')
wlandelay = time.ticks_ms() + 10000

pwm = PWM(Pin(16))
pwm.freq(20)
gy53 = Pin(15, Pin.IN)
IN1 = Pin(17, Pin.OUT)
IN2 = Pin(18, Pin.OUT)

currentFloor = 1
targetFloor = 1
dutycycle = 0

floorDistances = {
    1: 7500,  # Distance for 1st floor in microseconds
    2: 5000,  # Distance for 2nd floor in microseconds
    3: 2500  # Distance for 3rd floor in microseconds
}

# Check Wi-Fi connection
while time.ticks_ms() < wlandelay:
    if wlan.isconnected():
        if wlan.status() < 0 or wlan.status() >= 3:
            break
    machine.idle()

if wlan.status() != 3:
    raise RuntimeError('Wi-Fi connection failed')
    machine.reset()
else:
    print('Connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])
    wlan_mac = wlan.config('mac')
    print("MAC Address:", wlan_mac)  # Show MAC for peering

HOST = '0.0.0.0'
PORT = 5001
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
print(f"Listening for UDP messages on {HOST}:{PORT}")


# Function to simulate elevator movement
def move_elevator(floor):
    global currentFloor, targetFloor, dutycycle

    if floor == currentFloor:
        print("Already on the specified floor.")
        return

    # Determine the direction of movement
    direction = 1 if floor > currentFloor else -1

    # Set the motor direction based on the target floor
    if direction == 1:
        # Move up
        IN1.value(1)
        IN2.value(0)
    else:
        # Move down
        IN1.value(0)
        IN2.value(1)

    while True:
        distance = measureDistance()
        print("Distance:", distance)

        # Check if the elevator has reached the desired floor's distance
        if abs(distance - floorDistances[floor]) <= 100:  # Tolerance of 100 microseconds
            break

    # Update current floor and stop the motor
    currentFloor = floor
    IN1.value(0)
    IN2.value(0)
    dutycycle = 0
    sleep(1)  # Delay for the door opening or any other action


# Function to measure distance
def measureDistance():
    while gy53.value() == True:
        pass
    while gy53.value() == False:
        pass
    startTime = time.ticks_us()
    while gy53.value() == True:
        pass
    endTime = time.ticks_us()
    return endTime - startTime


# Main loop
while True:
    # Receiving and processing UDP messages
    data, addr = sock.recvfrom(1024)
    received_msg = data.decode('utf-8')  # Decode the received bytes to string
    print(f"Received message from {addr}: {received_msg}")

    # Assuming the received message is the target floor number (1, 2, or 3)
    try:
        target_floor = int(received_msg)
        if 1 <= target_floor <= 3:
            move_elevator(target_floor)
        else:
            print("Invalid floor number received:", target_floor)
    except ValueError:
        print("Invalid message received. Expecting floor number (1, 2, or 3)")

    # Rest of your code can remain empty as the elevator control is now solely based on UDP messages