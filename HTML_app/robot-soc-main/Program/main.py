from microdot import Microdot, send_file
from microdot.websocket import with_websocket
import subprocess
import logging
import os
import sys
import bloky
import RT_ovladani as RT

ADC_KONST = 65536

app = Microdot()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

STATIC_DIR = os.path.join(os.path.dirname(__file__))

def send_static_file(request, filename):
    try:
        file_path = os.path.join(STATIC_DIR, filename)
        return send_file(file_path)
    except Exception as e:
        logging.error(f"Error sending static file {filename}: {e}")
        return "Not Found", 404
    
@app.route('/')
async def index(request):
    return send_static_file(request, 'index.html')

@app.route('/styles.css')
async def styles(request):
    return send_static_file(request, 'styles.css')

@app.route('/bloky')
async def test(request):
    global index_s, test_s
    test_s = True
    index_s = False
    return send_static_file(request, 'control_bloky.html')

@app.route('/bloky.js')
async def bloky_js(request):
    return send_static_file(request, 'control_bloky.js')

@app.route('/rt')
async def rt_ovladani(request):
    global index_s, test_s
    index_s = True
    test_s = False
    return send_static_file(request, 'control_rt.html')

@app.route('/prijem')
@with_websocket
async def prijem(request, ws):
    try:
        #logging.info("WebSocket connected")
        await ws.send('Connected')
        
        while True:
            try:
                prijem = await ws.receive()
                if not prijem:
                    logging.warning("Received empty message")
                    continue
                    
                #logging.debug(f"Received message: {prijem}")
                parts = prijem.split()
                print(type(parts))
                
                if len(parts) > 4:
                    error_msg = f"Invalid message format: {prijem}"
                    logging.error(error_msg)
                    await ws.send(f"error: {error_msg}")
                    continue
                if len(parts) == 3:
                    command, smer, rychlost = parts
                elif len(parts) == 4:
                    command, smer, rychlost, cekani = parts
                
                print(type(command), type(smer), type(rychlost), type(cekani))
                #logging.info(f"Command: {command}, smer: {smer}, rychlost: {rychlost}, cekani: {cekani}")
                try:
                    rychlost = int((int(rychlost)/100)*65535)
                    await ws.send('ok')
                except ValueError as e:
                    error_msg = f"Invalid speed value: {rychlost}"
                    logging.error(error_msg)
                    await ws.send(f"error: {error_msg}")
                    continue
                except Exception as e:
                    error_msg = f"Error processing speed value: {e}"
                    logging.error(error_msg)
                    await ws.send(f"error: {error_msg}")
                    continue
                
                if index_s:
                    pohyb1(command, smer, rychlost)
                elif test_s:
                    cekani = int(cekani)
                    if cekani is None:
                        await ws.send("error: missing waiting time for test mode")
                        continue
                    pohyb2(smer, rychlost, cekani)
                
            except Exception as e:
                logging.error(f"Connection error: {e}")
                break

    finally:
        try:
            await ws.close()
        except:
            pass

def pohyb1(command, smer, rychlost):
    if smer == "0":
        RT.stop(command, smer, rychlost)
    elif smer == "1":
        RT.vpred(command, smer, rychlost)
    elif smer == "2":
        RT.vzad(command, smer, rychlost)
    elif smer == "3":
        RT.v_pravo(command, smer, rychlost)
    elif smer == "4":
        RT.v_levo(command, smer, rychlost)

def pohyb2(smer, rychlost, cekani):
    if smer == "0":
        bloky.stop(smer, rychlost, cekani)
    elif smer == "1":
        bloky.vpred(smer, rychlost, cekani)
    elif smer == "2":
        bloky.vzad(smer, rychlost, cekani)
    elif smer == "3":
        bloky.v_pravo(smer, rychlost, cekani)
    elif smer == "4":
        bloky.v_levo(smer, rychlost, cekani)
    
app.run(port=5000, debug=True)