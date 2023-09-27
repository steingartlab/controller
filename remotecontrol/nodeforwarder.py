"""Nodeforwarder is proftron Dan's invention,
a serial to RESTful API interface. This is an abstraction
on top of it to simplify the calling functions for all the
instruments we control through nfw.
"""

from functools import partial
from typing import Optional

import requests

from remotecontrol.docker import Container, BASE_IP

class NodeForwarder:

    def __init__(self, container: Container):
        self.container = container

        self.read = partial(self.execute, command='read')
        self.write = partial(self.execute, command='writecf')
        self.lastread = partial(self.execute, command='lastread')
        self.flushbuffer = partial(self.execute, command='flushbuffer')

    @property
    def url(self):
        return f'http://{BASE_IP}.{str(self.container.ip_ending)}:{str(self.container.port)}'
    
    def execute(self, command: str, payload: Optional[str] = None) -> None:
        url = f'{self.url}/{command}/{payload}'
        
        return requests.get(url).text
