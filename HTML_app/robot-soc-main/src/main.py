import asyncio
from microdot import Microdot, send_file
from microdot.websocket import with_websocket
import network
import socket
from time import sleep
#import machine
#import rp2
import sys
import stepper
import logging

logging.basicConfig(level=logging.DEBUG)
ssid = 'name-rsoc'
password = 'idk123456'

KROK_PIN = [18, 19, 20, 21]

MOT1_PIN = [16, 17]
MOT2_PIN = [22, 26]
#motor1 = Pin(MOT1_PIN[0], Pin.OUT)
"""motor1_r = machine.PWM(machine.Pin(MOT1_PIN[0]), freq=2000)
motor1_f = machine.PWM(machine.Pin(MOT1_PIN[1]), freq=2000)

motor2_r = machine.PWM(machine.Pin(MOT2_PIN[0]), freq=2000)
motor2_f = machine.PWM(machine.Pin(MOT2_PIN[1]), freq=2000)"""

#motor2 = Pin(MOT2_PIN[0], Pin.OUT)
#motor2_pwm = PWM(Pin(MOT2_PIN[1]), freq=2000)

async def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        await asyncio.sleep(1)

    print(wlan.ifconfig())

async def ap_mode(ssid, password):
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    ap.active(True)

    while ap.active() == False:
        pass
    print('AP Mode Is Active, You can Now Connect')
    print('IP Address To Connect to:: ' + ap.ifconfig()[0])

def stepper_initialize():
    stepper_motor = stepper.HalfStepMotor.frompins(KROK_PIN[0], KROK_PIN[1], KROK_PIN[2], KROK_PIN[3])

    stepper_motor.reset()

app = Microdot()

@app.route('/')
async def index(request):
    try:
        #file_path = os.path.join(os.path.dirname(__file__), 'index.html')
        return send_file('index.html')
    except Exception as e:
        logging.error(f"Error in index route: {e}")
        return "Internal Server Error", 500


@app.route('/bloky')
async def bloky(request):
    return send_file(request, 'control_bloky.html')

@app.route('/bloky.js')
async def bloky_js(request):
    return send_file(request, 'control_bloky.js')

@app.route('/styles.css')
async def styles(request):
    return send_file(request, 'styles.css')



@app.route('/rt')
async def rt_ovladani(request):
    return send_file(request, 'control_rt.html')




@app.route('/prijem')
@with_websocket
async def prijem(request, ws):
    #global command, smer, rychlost
    try:
        while True:
            prijem = await ws.receive()
            #logging.debug(f"Received message: {prijem}")
            parts = prijem.split()
            #print(parts)
            command = parts[0]
            smer = int(parts[1])
            rychlost = int((int(parts[2])/100)*65535)
            
            pohyb(command, smer, rychlost)
            
    except Exception as e:
        logging.error(f"Error in prijem route: {e}")
        pass

def pohyb(command, smer, rychlost):
    def vpred(command, rychlost):
        if command == 'start':
            print(f"Směr: {smer}")
            print(f"Rychlost: {rychlost}")
            """motor1_f.duty_u16(rychlost)
            motor1_r.duty_u16(0)
            motor2_f.duty_u16(rychlost)
            motor2_r.duty_u16(0)"""

    
    def vzad(command, rychlost):
        if command == 'start':
            print(f"Směr: {smer}")
            print(f"Rychlost: {rychlost}")
            """motor1_f.duty_u16(0)
            motor1_r.duty_u16(rychlost)
            motor2_f.duty_u16(0)
            motor2_r.duty_u16(rychlost)"""


    
    def v_pravo(command, rychlost):
        if command == 'start':
            print(f"Směr: {smer}")
            print(f"Rychlost: {rychlost}")
            """motor1_f.duty_u16(0)
            motor1_r.duty_u16(rychlost)
            motor2_f.duty_u16(rychlost)
            motor2_r.duty_u16(0)
            stepper_motor.step(50)"""

    
    def v_levo(command, rychlost):
        if command == 'start':
            print(f"Směr: {smer}")
            print(f"Rychlost: {rychlost}")
            """motor1_f.duty_u16(rychlost)
            motor1_r.duty_u16(0)
            motor2_f.duty_u16(0)
            motor2_r.duty_u16(rychlost)
            stepper_motor.step(-50)"""



    def stop():
        print("stop")
        """motor1_f.duty_u16(0)
        motor1_r.duty_u16(0)
        motor2_f.duty_u16(0)
        motor2_r.duty_u16(0)"""


    if smer == 1:
        vpred(command, rychlost)
    elif smer == 2:
        vzad(command, rychlost)
    elif smer == 3:
        v_pravo(command, rychlost)
    elif smer == 4:
        v_levo(command, rychlost)
    elif smer == 0:
        stop()

async def main():

    stepper_initialize()

    #await connect()
    await ap_mode(ssid, password)
    # start the server in a background task
    server = asyncio.create_task(app.start_server())

    # ... do other asynchronous work here ...
    
    # cleanup before ending the application
    await server

asyncio.run(main())
