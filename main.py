# Nombre del ejercicio, mi nombre

from textwrap import indent
import psutil
import time
import signal
import sys
import requests
import urllib
import json
import urllib.parse #CUIDADO HE CAMBIADO ESTO

ram_str_percent = ""
cpu_str = ""
api_key_write = ""
channel_id = ""
personal_key = "RCNT1IDF2IBPZPFM"
channel_count = 0
name = ""

def calc_cpu_ram():
    cpu = psutil.cpu_percent(0.0, False)
    ram = psutil.virtual_memory()
    ram_str = str(ram).split(", ")[2]
    global ram_str_percent
    ram_str_percent = ram_str.split('=')[1]
    global cpu_str
    cpu_str = str(cpu)


def cpu_ram_send():
    calc_cpu_ram()
    print("CPU: %" + cpu_str + "\tRAM: %" + ram_str_percent)
    send_petition(cpu_str, ram_str_percent)
    time.sleep(15)


def handler(sig_num, frame):
    print('\nSignal handler called with signal ' + str(sig_num))
    get_vals()
    clear_channel()
    print('\nExisting gracefully')
    sys.exit(0)


def get_vals():
    metodo = 'GET'
    uri = "https://api.thingspeak.com/channels/" + str(channel_id) + "/feeds.json"
    cabeceras = {'Host': 'api.thingspeak.com',
                 'Content-Type': 'application/x-www-form-urlencoded'}
    cuerpo = {'api_key': api_key_write}
    response = requests.request(metodo, uri, data=cuerpo, headers=cabeceras, allow_redirects=False)
    content_dict = json.loads(response.content)
    with open('json_data.json', 'w') as outfile:
        json.dump(content_dict, outfile, ensure_ascii = False, indent= 4)
    


def send_petition(param1, param2):
    metodo = 'POST'
    uri = "https://api.thingspeak.com/update"
    cabeceras = {'Host': 'api.thingspeak.com',
                 'Content-Type': 'application/x-www-form-urlencoded'}
    cuerpo = {'api_key': api_key_write,
              'field1': param1,
              'field2': param2}
    requests.request(metodo, uri, data=cuerpo, headers=cabeceras, allow_redirects=False)
    
    
def clear_channel():
    metodo = 'DELETE'
    uri = "https://api.thingspeak.com/channels/" + str(channel_id) + "/feeds.json"
    cabeceras = {'Host': 'api.thingspeak.com',
                 'Content-Type': 'application/x-www-form-urlencoded'}
    cuerpo = {'api_key': personal_key}
    requests.request(metodo, uri, data=cuerpo, headers=cabeceras, allow_redirects=False)

    
def create_channel():
    calc_cpu_ram()
    metodo = 'POST'
    uri = "https://api.thingspeak.com/channels.json"
    cabeceras = {'Host': 'api.thingspeak.com',
                 'Content-Type': 'application/x-www-form-urlencoded'}
    cuerpo = {'api_key': personal_key,
              'name': name,
              'field1': cpu_str,
              'field2': ram_str_percent}
    contenido_encoded = urllib.parse.urlencode(cuerpo)
    cabeceras['Content-Length'] = str(len(contenido_encoded)) 
    respuesta = requests.request(metodo, uri, data=contenido_encoded, headers=cabeceras, allow_redirects=False)
    
    content = respuesta.content
    content_dict = json.loads(content)
    global api_key_write
    keys = content_dict['api_keys']
    api_key_write = keys[0]['api_key']
    global channel_id
    channel_id = content_dict['id']


def channel_exists(name):
    exists = False
    count = 0
    metodo = 'GET'
    uri = "https://api.thingspeak.com/channels.json"
    cabeceras = {'Host': 'api.thingspeak.com',
                 'Content-Type': 'application/x-www-form-urlencoded'}
    cuerpo = {'api_key': personal_key}
    response = requests.request(metodo, uri, data=cuerpo, headers=cabeceras, allow_redirects=False)
    
    content = response.content
    content_dict = json.loads(content)
    for channel in content_dict:
        if channel['name'] == name:
            global api_key_write
            api_key_write = channel['api_keys'][0]['api_key']
            global channel_id
            channel_id = channel['id']
            exists = True
        count += 1
    global channel_count
    channel_count = count
    return exists
    

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    print('Running. Press CTRL-C to exit.')
    name = input("Type a name for your channel:\n")
    if (channel_exists(name) == False):
        if (channel_count < 4):
            create_channel()
        else:
            print("Channel limit reached")
    else:
        print("A channel with that name exists\nThe information will be sent there")
    while True:
        cpu_ram_send()
