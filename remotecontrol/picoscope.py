"""Interface with oscilloscopes from PicoTech, called picoscopes."""

from dataclasses import asdict, dataclass
import json
from typing import Dict, List

import requests


with open('docker.json', 'r') as json_file:
    containers = json.load(json_file)


URL: str = f"http://192.168.0.{containers['picoscope']['ip']}:{containers['picoscope']['port']}/get_wave"


# @dataclass#(kw_only) <- TODO: Implement when py3.10
# class Picoscope:
#     """All the params that should should be passed
#     to a pulsing picoscope, no more, no less.

#     Change at your leisure.
#     """

#     delay: float
#     duration: float
#     voltage_range: float
#     avg_num: int = 64


def callback(pulsing_params: Dict[str, float]) -> Dict[str, List[float]]:
    """Queries data from oscilloscope.
    
    Args:
        pulsing_params (Picoscope): See Picoscope.
        
    Returns:
        dict[str: list[float]]: Single key-value pair with key='data' and value
            acoustics pulse data.
    """

    response = requests.post(URL, data=pulsing_params).text
    
    return json.loads(response)
