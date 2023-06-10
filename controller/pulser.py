from functools import partial

import requests

import config
from controller.utils import make_url

IP = config.pulser['ip']
PORT = config.pulser['port']

def _send(command: str, message: str = '') -> None:
    url = make_url(IP, PORT)

    return requests.get(f'{url}/{command}/{message}').text
        

write = partial(_send, 'writecf')
turn_on = partial(write, 'P500')
turn_off = partial(write, 'P0')