# Nombre del ejercicio, mi nombre

import psutil
import time
import signal
import sys
import requests
import urllib


def cpu_ram():
    cpu = psutil.cpu_percent(0.0, False)
    ram = psutil.virtual_memory()
    ram_str = str(ram).split(", ")[2]
    ram_str_percent = ram_str.split('=')[1]
    cpu_percent = str(cpu)
    print("CPU: %" + cpu_percent + "\tRAM: %" + ram_str_percent)
    send_petition(cpu_percent, ram_str_percent)
    time.sleep(15)


def handler(sig_num, frame):
    print('\nSignal handler called with signal ' + str(sig_num))
    print('Check signal number on https://en.wikipedia.org/wiki/Signal_%28IPC%29#Default_action')
    print('\nExisting gracefully')
    sys.exit(0)


def send_petition(cpu_str, ram_str):
    metodo = 'POST'
    uri = "https://api.thingspeak.com/update.json"
    cabeceras = {'Host': 'api.thingspeak.com',
                 'Content-Type': 'application/x-www-form-urlencoded'}
    cuerpo = "api_key=RU3U0L7OB9SAL87K&field1=" + cpu_str + "&field2=" + ram_str
    print(cuerpo) #DATOS COMO DICCIONARIO
    respuesta = requests.request(metodo, uri, data=cuerpo, headers=cabeceras, allow_redirects=False)

    print(str(respuesta.status_code))


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    print('Running. Press CTRL-C to exit.')
    while True:
        cpu_ram()
