from dataclasses import dataclass
from enum import auto
import logging
import threading
from time import time

from controller import utils
from controller.database import Database
from controller.instruments import Picoscope, Pulser, PicoParams


@dataclass
class Settings:
    duration: float  # h
    interval: float  # s
    exp_id: str
    pico: dict[str, float] | PicoParams

    def set_pico(self) -> None:
        self.pico = utils.dataclass_from_dict(
            dataclass_=PicoParams,
            dict_=self.pico
        )


class Status(utils.ZeroBasedAutoEnum):
    not_started = auto()
    running = auto()
    stopped = auto()


class Controller:
    def __init__(self):
        self.start = time()
        self.pill = threading.Event()
        self._status = Status(0)
    
    @property
    def status(self) -> str:
        return self._status.name

    @property
    def time_elapsed(self) -> float:
        return time() - self.start

    def loop(self, settings: Settings) -> None: 
        picoscope: Picoscope = Picoscope(params=settings.pico)
        self.database: Database = Database(db_filename=settings.exp_id)    
        self._status = Status(1)

        while self.time_elapsed < settings.duration and not self.pill.wait(settings.interval):
            try:
                waveform: dict[str, list[float]] = _pulse(picoscope=picoscope)
                row_id = self.save(waveform=waveform)
                logging.info(f'Pulse completed. Row id: {row_id}')

            except Exception as e:
                logging.error(e)

        self._status = Status(2)

    def pulse(self) -> dict[str, list[float]]:
        """Single pulse."""
        
        picoscope: Picoscope = Picoscope(params=settings.pico)
        
        return _pulse(picoscope=Picoscope)


    def save(self, waveform: dict[str, list[float]]) -> int:
        timestamp: dict[str, float] = {'time': time()}
        waveform.update(timestamp)
        query: str = self.database.parse_query(payload=waveform)
        row_id: int = self.database.write(query)

        return row_id

    def stop(self):
        """Manually stop experiment."""
        self.pill.set()


def _pulse(picoscope: Picoscope) -> dict[str, list[float]]:
    """Wrapper."""
    pulser = Pulser()
    pulser.turn_on()
    waveform: dict[str, list[float]] = picoscope.callback()
    pulser.turn_off()

    return waveform

    