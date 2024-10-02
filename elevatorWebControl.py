try:
  import usocket as socket
except:
  import socket
        
from machine import Pin, PWM
import network
import time

ssid = 'ITEK 1st'
password = 'iteke23a'

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

frequency = 6500
dutycycle = 0.7

pwm = PWM(Pin(16))
pwm.freq(frequency)
gy53 = Pin(19, Pin.IN)
IN1 = Pin(17, Pin.OUT)
IN2 = Pin(18, Pin.OUT)

tolerance = 100
currentFloor = 1
targetFloor = 1

floorDistances = {
    1: 1850,  # Distance for 1st floor in microseconds
    2: 1100,  # Distance for 2nd floor in microseconds
    3: 400  # Distance for 3rd floor in microseconds
}

floorNames = {
    1: "Stueetagen",  # Distance for 1st floor in microseconds
    2: "1. sal",  # Distance for 2nd floor in microseconds
    3: "2. sal"  # Distance for 3rd floor in microseconds
}

def move_elevator(floor):
    global currentFloor, targetFloor, dutycycle, frequency

    if floor == currentFloor:
        print("Already on the specified floor.")
        return

    # Determine the direction of movement
    direction = 1 if floor > currentFloor else -1

    # Set the motor direction based on the target floor
    if direction == 1:
        # Move up
        # dutycycle += 0.55

        IN1.value(1)
        IN2.value(0)
        # time.sleep(0.05)
        # dutycycle -= 0.55

    else:
        # Move down
        dutycycle -= 0.68
        IN1.value(0)
        IN2.value(1)

    while True:
        

        distance = measureDistance()
        print(distance/100)


        # Check if the elevator has reached the desired floor's distance
        if abs(distance - floorDistances[floor]) <= tolerance:  # Tolerance of 100 microseconds
            if direction == -1:
                dutycycle += 0.68
                IN1.value(1)
                IN2.value(0)
                time.sleep(0.1)
            if direction == 1:
                IN1.value(0)
                IN2.value(1)
                time.sleep(0.05)
            break

    # Update current floor and stop the motor
    currentFloor = floor
    IN1.value(0)
    IN2.value(0)

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

def web_page():

    html = """<html>

<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css"
     integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
    <link href="https://fonts.googleapis.com/css2?family=Ubuntu+Mono:wght@700&display=swap" rel="stylesheet">
    <style>
    html {
        font-family: 'Ubuntu Mono', monospace;
        display: inline-block;
        margin: 0px auto;
        text-align: center;
    }

    body {
        font-family: 'Ubuntu Mono', monospace;
        position: relative;
    }

    body::before {
        content: '';
        display: block;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url('https://pbs.twimg.com/media/FyDgv8eXwAEkBhF.jpg');
        background-size: cover;
        background-repeat: no-repeat;
        opacity: 0.8;
        z-index: -1;
    }

    .button {
        font-family: 'Ubuntu Mono', monospace;
        background-color: #ce1b0e;
        border: none;
        color: white;
        padding: 24px 80px; /* Increase width to 80px */
        width: 20%; /* Set a wider width of 20% */
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 18px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
        transition: opacity 0.3s ease;
    }

    .button:hover {
        opacity: 0.85;
    }

    #text {
        color: black;
        font-size: 18px;
    }
    </style>
</head>
<body>
    <h2>Elevatoren</h2>
    <p id="text">Etage: <strong>"""+ floorNames[currentFloor] + """</strong></p>
    <p>
        <a href=\"andenSal\"><button class="button">2. Sal</button></a>
        <a></a>
    </p>
    <p>
        <a href=\"foersteSal\"><button class="button">1. Sal</button></a>
        <a></a>
    </p>
    <p>
        <a href=\"stueetage\"><button class="button">Stueetage</button></a>
        <a></a>
</body>
</html>"""
    return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)
conn = 0

while True:
    pwm.duty_u16(int(65536 * dutycycle))
    try:
        conn, addr = s.accept()
        conn.settimeout(3.0)
        request = conn.recv(1024)
        conn.settimeout(None)
        request = str(request)
        stueetage = request.find('/stueetage')
        førstesal = request.find('/foersteSal')
        andensal = request.find('/andenSal')

        if stueetage == 6:
            move_elevator(1)
        if førstesal == 6:
            move_elevator(2)
        if andensal == 6:
            move_elevator(3)
        
        response = web_page()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n  \n')
        conn.sendall(response)
        conn.close()
    except OSError as e:
        conn.close()
        print('Connection closed') 