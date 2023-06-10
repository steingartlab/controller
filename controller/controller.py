from dataclasses import dataclass
from enum import auto
import threading
from time import time
from typing import Dict, Union

from controller import picoscope, pulser, utils
from controller.database import Database


@dataclass
class ExpSettings:
    duration: float  # zh
    interval: float  # s
    exp_id: str


class Status(utils.ZeroBasedAutoEnum):
    not_started = auto()
    running = auto()
    stopped = auto()
    error = auto()


class Controller:
    def __init__(self):
        self.start = time()
        self.pill = threading.Event()
        self._status = Status(0)
    
    @property
    def status(self) -> str:
        return self._status.name

    @status.setter
    def status(self, num):
        self._status = num

    @property
    def last_updated(self) -> str:
        return utils.last_folder_update()

    @property
    def time_elapsed(self) -> float:
        return time() - self.start

    def _loop(self, exp_settings: ExpSettings):
        
        while self.time_elapsed < settings.duration and not self.pill.wait(exp_settings.interval):
            try:
                waveform: dict[str, list[float]] = _pulse(picoscope=picoscope)
                row_id = self.save(waveform=waveform)
                logging.info(f'Pulse completed. Row id: {row_id}')
                self._status = 1

            except Exception as e:
                logging.error(e)
                self._status = 3

    def pulse(self, pico_params) -> dict[str, list[float]]:
        """Single pulse."""

        return _pulse(pico_params)

    def start(self, exp_settings: ExpSettings, pico_params: picoscope.PicoParams) -> None: 
        picoscope: Picoscope = Picoscope(params=pico_params)
        self.database: Database = Database(db_filename=exp_settings.exp_id)    
        self._status = 1
        self._loop(exp_settings)
        self._status = 2

    def save(self, waveform: dict[str, list[float]]) -> int:
        timestamp: dict[str, float] = {'time': time()}
        waveform.update(timestamp)
        query: str = self.database.parse_query(payload=waveform)

        return self.database.write(query)

    def stop(self):
        """Manually stop experiment."""
        self.pill.set()


def _pulse(pico_params: picoscope.PicoParams) -> dict[str, list[float]]:
    """Wrapper."""
    pulser.turn_on()
    waveform: dict[str, list[float]] = picoscope.callback(pico_params)
    pulser.turn_off()

    return waveform

    
