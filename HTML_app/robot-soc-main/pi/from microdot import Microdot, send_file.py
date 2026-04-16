from microdot import Microdot, send_file
from microdot.websocket import with_websocket
import machine
import time
import network
#import subprocess
import logging
#import os
    
ADC_KONST = 65536
#MOT1_PIN = [10, 11]
#MOT2_PIN = [12, 13]
#motor1 = Pin(MOT1_PIN[0], Pin.OUT)
#motor1_pwm = PWM(Pin(MOT1_PIN[1]), freq=2000)
#motor2 = Pin(MOT2_PIN[0], Pin.OUT)
#motor2_pwm = PWM(Pin(MOT2_PIN[1]), freq=2000)

app = Microdot()

# Configure logging
#logging.basicConfig(level=logging.DEBUG)

@app.route('/')
async def index(request):
    try:
        #file_path = os.path.join(os.path.dirname(__file__), 'index.html')
        return send_file('index.html')
    except Exception as e:
        logging.error(f"Error in index route: {e}")
        return "Internal Server Error", 500

@app.route('/prijem')
@with_websocket
async def prijem(request, ws):
    #global command, smer, rychlost
    try:
        while True:
            prijem = await ws.receive()
            logging.debug(f"Received message: {prijem}")
            parts = prijem.split()
            command = parts[0]
            smer = int(parts[1])
            rychlost = int((int(parts[2])/100)*65535)
            
            pohyb(command, smer, rychlost)
            
    except Exception as e:
        logging.error(f"Error in prijem route: {e}")

def pohyb(command, smer,  rychlost):
    #nonlocal command, smer, rychlost 
    def vpred(command, rychlost):
        if command == 'start':
            subprocess.run("cls" if os.name == "nt" else "clear", shell=True)
            logging.info("Start command received")
            try:
                logging.info(f"Směr: {smer}")
                logging.info(f"Rychlost: {rychlost}")
            except ValueError:
                logging.error(f"Invalid command received: {prijem}")
        elif command == 'stop':
            logging.info("Stop command received")
            logging.info(f"Motor: {smer}")
            logging.info(f"Rychlost: {rychlost}")
            #motor1.duty_u16(rychlost)
            print(f"Motor1 spusten, pwm:{rychlost}")
            #motor2.duty_u16(rychlost)
            print(f"Motor2 spusten, pwm:{rychlost}")
        
    def vzad(command, rychlost):
        if command == 'start':
            subprocess.run("cls" if os.name == "nt" else "clear", shell=True)
            logging.info("Start command received")
            try:
                logging.info(f"Směr: {smer}")
                logging.info(f"Rychlost: {rychlost}")
            except ValueError:
                logging.error(f"Invalid command received: {prijem}")
        elif command == 'stop':
            logging.info("Stop command received")
            logging.info(f"Motor: {smer}")
            logging.info(f"Rychlost: {rychlost}")
            #motor1.duty_u16(rychlost)
            print(f"Motor1 spusten, pwm:{rychlost}")
            #motor2.duty_u16(rychlost)
            print(f"Motor2 spusten, pwm:{rychlost}")

    def v_pravo(command, rychlost):
        if command == 'start':
            subprocess.run("cls" if os.name == "nt" else "clear", shell=True)
            logging.info("Start command received")
            try:
                logging.info(f"Směr: {smer}")
                logging.info(f"Rychlost: {rychlost}")
            except ValueError:
                logging.error(f"Invalid command received: {prijem}")
        elif command == 'stop':
            logging.info("Stop command received")
            logging.info(f"Motor: {smer}")
            logging.info(f"Rychlost: {rychlost}")
            #motor1.duty_u16(rychlost)
            print(f"Motor1 spusten, pwm:{rychlost}")
            #motor2.duty_u16(rychlost)
            print(f"Motor2 spusten, pwm:{rychlost}")

    def v_levo(command, rychlost):
        if command == 'start':
            subprocess.run("cls" if os.name == "nt" else "clear", shell=True)
            logging.info("Start command received")
            try:
                logging.info(f"Směr: {smer}")
                logging.info(f"Rychlost: {rychlost}")
            except ValueError:
                logging.error(f"Invalid command received: {prijem}")
        elif command == 'stop':
            logging.info("Stop command received")
            logging.info(f"Motor: {smer}")
            logging.info(f"Rychlost: {rychlost}")
            #motor1.duty_u16(rychlost)
            print(f"Motor1 spusten, pwm:{rychlost}")
            #motor2.duty_u16(rychlost)
            print(f"Motor2 spusten, pwm:{rychlost}")
        
    if smer == 1:
        vpred(command, rychlost)
    elif smer == 2:
        vzad(command, rychlost)
    elif smer == 3:
        v_pravo(command, rychlost)
    elif smer == 4:
        v_levo(command, rychlost)

# if you do not see the network you may have to power cycle
# unplug your pico w for 10 seconds and plug it in again
def ap_mode(ssid, password):
    """
        Description: This is a function to activate AP mode

        Parameters:

        ssid[str]: The name of your internet connection
        password[str]: Password for your internet connection

        Returns: Nada
    """
    # Just making our internet connection
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    ap.active(True)

    while ap.active() == False:
        pass
    print('AP Mode Is Active, You can Now Connect')
    print('IP Address To Connect to:: ' + ap.ifconfig()[0])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #creating socket object
    s.bind(('', 80))
    s.listen(5)

    while True:
      conn, addr = s.accept()
      print('Got a connection from %s' % str(addr))
      request = conn.recv(1024)
      print('Content = %s' % str(request))
      response = web_page()
      conn.send(response)
      conn.close()

async def main():
    # start the server in a background task
    server = asyncio.create_task(app.start_server(port=5000, debug=true))
    
    ap_mode('name','pass')
    # ... do other asynchronous work here ...

    # cleanup before ending the application
    await server

asyncio.run(main())


#ap_mode('NAME','PASSWORD')
#app.run(port=5000, debug=True)

