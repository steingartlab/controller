"""Interface with Cytec CXAR/128 multiplexer.
Well, it probably works for other Cytec models as wells.
"""

from dataclasses import dataclass
import json
from typing import Optional

from remotecontrol.nodeforwarder import NodeForwarder

with open('docker.json', 'r') as json_file:
    containers = json.load(json_file)


mux_: NodeForwarder = NodeForwarder(container=containers['mux'])


@dataclass
class Channel:
    switch: int
    module: Optional[int] = 0


def parse(module: int, switch: int) -> str:
    """We exclusively use the Mux command (X)
    because it auto-unlatches the module/switch the
    next time it is called for a different one, reducing
    the mux commands sent by a factor of two.
    """
    return f'X{str(module)},{str(switch)}'


def mux(channel: Channel):    
    payload = parse(module=channel.module, switch=channel.switch)
    mux_.write(payload=payload)


def clear():
    """Generally not needed, but may be useful in some cases. Unlatches everything."""
    mux_.write('C')