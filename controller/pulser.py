"""Methods for interfacing with pulsers from Ultratek.

See https://github.com/steingartlab/nodeforwarder.

Example:
    from controller import pulser

    pulser.turn_on()
    # do picoscope stuff
    pulser.turn_off()
"""

from functools import partial

import requests

import config
from controller.utils import make_url


IP = config.pulser['ip']
PORT = config.pulser['port']


def _send(command: str, message: str = '') -> None:
    """Send commands to pulser using nodeforwarder."""
    
    url = make_url(IP, PORT)

    return requests.get(f'{url}/{command}/{message}').text
        

_write = partial(_send, 'writecf')
# Not implemented for pulser bc we never read anything from it
# (but used for other nodeforwarder instrument applications).
# _read = partial(_send, 'read')

turn_on = partial(_write, 'P500')
turn_off = partial(_write, 'P0')