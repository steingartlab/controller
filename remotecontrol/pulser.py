"""Interface with Ultratek Pulser over nodeforwarder."""

from dataclasses import dataclass
from functools import partial
import json
from typing import Callable, Optional

from remotecontrol.nodeforwarder import NodeForwarder


with open('docker.json', 'r') as json_file:
    containers = json.load(json_file)


pulser: NodeForwarder = NodeForwarder(container=containers['pulser'])
PRF = 'P500'  # Pulse repetition rate
turn_on: Callable[[], str] = partial(pulser.write, payload=PRF)
turn_off: Callable[[], str] = partial(pulser.write, payload='P0')


class Properties:
    """These properties need to be tweaked for each use case."""

    def __init__(self, gain_dB: int, transducer_frequency_MHz: Optional[float] = 2.25, mode: Optional[int] = 1):
        self.mode: str = f'M{mode}'
        
        pulse_width_ns: str = self.parse_pulse_width(transducer_frequency_MHz)
        self.pulse_width: str = f'W{pulse_width_ns}'
        
        gain_parsed = self.parse_gain(gain_dB)
        self.gain: str = f'G{gain_parsed}' # In 1/10 of actual, so G300 is 30 dB

    @staticmethod
    def parse_pulse_width(transducer_frequency_MHz: float) -> str:
        pulse_width_ns = (1 / transducer_frequency_MHz) * 1e3

        return str(int(pulse_width_ns))

    @staticmethod
    def parse_gain(gain_dB: int) -> int:
        """"""
        return int(gain_dB * 10)


@dataclass
class Config:
    """These parameters are only used for initial setup and should
    thus not be called during experiments.
    """
    pulse_repetition_rate: str = 'P500'  # In 1/10 of actual, so P500 is 5000 Hz
    damping: str = 'D7'  # D7 is maximum damping
    pulse_voltage: str = 'V350'  # In actual volts
    trigger_type: str = 'T0'  # internal


def set_properties(properties: Properties):    
    for message in vars(properties).values():
        pulser.write(payload=message)
