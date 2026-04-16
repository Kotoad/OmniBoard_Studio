import logging
import os
import subprocess
from time import sleep
logging.basicConfig(level=logging.DEBUG)

def stop(smer, rychlost, cekani):
    #logging.info("Stop command received")
    #logging.info(f"Směr: {smer}")
    #logging.info(f"Rychlost: {rychlost}")
    #logging.info(f"Čekání: {cekani}")
    sleep(int(cekani))

def vpred(smer, rychlost, cekani):
    # subprocess.run("cls" if os.name == "nt" else "clear", shell=True)
    #logging.info("Start command received")
    #logging.info(f"Směr: {smer}")
    #logging.info(f"Rychlost: {rychlost}")
    #logging.info(f"Čekání: {cekani}")
    sleep(int(cekani))

def vzad(smer, rychlost, cekani):
    # subprocess.run("cls" if os.name == "nt" else "clear", shell=True)
    #logging.info("Start command received")
    #logging.info(f"Směr: {smer}")
    #logging.info(f"Rychlost: {rychlost}")
    #logging.info(f"Čekání: {cekani}")
    sleep(int(cekani))

def v_pravo(smer, rychlost, cekani):
    # subprocess.run("cls" if os.name == "nt" else "clear", shell=True)
    #logging.info("Start command received")
    #logging.info(f"Směr: {smer}")
    #logging.info(f"Rychlost: {rychlost}")
    #logging.info(f"Čekání: {cekani}")
    sleep(int(cekani))

def v_levo(smer, rychlost, cekani):
    # subprocess.run("cls" if os.name == "nt" else "clear", shell=True)
    #logging.info("Start command received")
    #logging.info(f"Směr: {smer}")
    #logging.info(f"Rychlost: {rychlost}")
    #logging.info(f"Čekání: {cekani}")
    sleep(int(cekani))