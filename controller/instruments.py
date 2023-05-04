from dataclasses import asdict, dataclass, fields
import json
from time import sleep

import requests


@dataclass
class PicoParams:
    """All the params that should should be passed
    to a pulsing picoscope, no more, no less.

    Change at your leisure.
    """

    delay: int = 26
    voltage_range: float = 0.5
    duration: int = 6


@dataclass
class PulserProperties:
    """Everything needed to configure Ultratek pulser."""
    damping: str = 'D7'
    mode: str = 'M0'
    pulse_voltage: str = 'V350'
    pulse_width: str = 'W222'
    pulse_repetition_rate: str = 'P500'
    mode: str = 'T0'  # internal triggering


class Picoscope:
    """Need for speed"""

    ip_: str = '192.168.0.10'
    port: str = '5001'
    url = f'http://{ip_}:{port}/get_wave'

    def __init__(self, params: PicoParams):
        self.params: dict[str, float] = asdict(params)

    def callback(self) -> dict[str, list[float]]:
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

        response = requests.post(Picoscope.url, data=self.params).text

        return json.loads(response)



class Pulser():
    """Methods for interfacing with Ultratek pulser."""

    IP = '192.168.0.20'
    PORT = '9002'

    def __init__(self):
        self.url = f"http://{Pulser.IP}:{Pulser.PORT}"

    def _send(self, command: str) -> None:
        requests.get(f'{self.url}/writecf/{command}').text

    def read(self):
        feedback = requests.get(f'{self.url}/read').text
        print(feedback)

    def config(self, pulser_properties: PulserProperties):
        for field in fields(pulser_properties):
            value = getattr(pulser_properties, field.name)
            self._send(command=value)
            sleep(.5)
        
    def turn_on(self, prf: str = 'P500') -> None:
        """Turns pulser on.
        
        Args:
            prf (str, optional): Pulse repetition frequency.
                Defaults to P500, which is equivalent to
                5 kHz (P is in 10s of Hz).
        """
        self._send(command=prf)

    def turn_off(self) -> None:
        """Turns pulser off"""
        self._send(command='P0')

