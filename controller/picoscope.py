from dataclasses import asdict, dataclass
import json
from typing import Dict, List

import requests

import config
from controller.utils import make_url

IP = config.picoscope['ip']
PORT = config.picoscope['port']


@dataclass
class PicoParams:
    """All the params that should should be passed
    to a pulsing picoscope, no more, no less.

    Change at your leisure.
    """

    delay: int
    voltage_range: float
    duration: int


def callback(pico_params: PicoParams) -> Dict[str, List[float]]:
    """Queries data from oscilloscope.
    
    Args:
        PulsingParams (dataclass): See definition at top of module. 
        ip_ (str, optional): IP address of oscilloscope container.
            Defaults to '192.168.0.1'.
        port (str, optional): Exposed port of oscilloscope container.
            Defaults to '5001'.
    
    Returns:
        dict[str: list[float]]: Single key-value pair with key='data' and value
            acoustics pulse data.
    """

    url = make_url(IP, PORT)
    response = requests.post(f'{url}/get_wave', data=asdict(pico_params)).text

    return json.loads(response)


