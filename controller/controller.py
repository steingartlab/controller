from dataclasses import dataclass
from enum import auto
import logging
import os
import threading
from time import sleep, time
from typing import Dict, Union

from controller import picoscope, pulser, utils
from controller.database import Database


log_filename = "logs/logs.log"
os.makedirs(os.path.dirname(log_filename), exist_ok=True)
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s: %(message)s'
)


@dataclass
class ExpSettings:
    exp_duration_h: float  # h
    interval: float  # s
    exp_id: str

    @property
    def exp_duration_s(self):
        return self.exp_duration_h * 3600


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
        return self._status

    @status.setter
    def status(self, num):
        self._status = num

    @property
    def last_updated(self) -> str:
        return utils.last_folder_update()

    @property
    def time_elapsed(self) -> float:
        return time() - self.start

    def _loop(self, exp_settings: ExpSettings, pico_params: picoscope.PicoParams):

        while self.time_elapsed < exp_settings.exp_duration_s and not self.pill.wait(exp_settings.interval):
            try:
                waveform: dict[str, list[float]] = _pulse(pico_params=pico_params)
                row_id = self.save(waveform=waveform)
                logging.info(f'Pulse completed. Row id: {row_id}')
                self._status = 1

            except Exception as e:
                logging.error(e)
                self._status = 3
                sleep(10)

    def start(self, exp_settings: ExpSettings, pico_params: picoscope.PicoParams) -> None: 
        self.database: Database = Database(db_filename=exp_settings.exp_id)    
        self._status = 1
        self._loop(exp_settings=exp_settings, pico_params=pico_params)
        self._status = 2

    def save(self, waveform: dict[str, list[float]]) -> int:
        timestamp: dict[str, float] = {'time': time()}
        waveform.update(timestamp)
        query: str = self.database.parse_query(payload=waveform)

        return self.database.write(query)

    def stop(self):
        """Manually stop experiment."""
        self.pill.set()
        self.pill = threading.Event()
        self._status = 2

def _pulse(pico_params: picoscope.PicoParams) -> dict[str, list[float]]:
    """."""

    pulser.turn_on()
    waveform: dict[str, list[float]] = picoscope.callback(pico_params)
    pulser.turn_off()

    return waveform


def pulse(incoming: dict[str, str]) -> dict[str, list[float]]:
    pico_params: PicoParams = utils.dataclass_from_dict(
        dataclass_=picoscope.PicoParams,
        dict_=incoming
    )

    return _pulse(pico_params)


def start_thread(controller_: Controller, incoming: dict[str, str]) -> None:
    exp_settings: ExpSettings = utils.dataclass_from_dict(
        dataclass_=ExpSettings,
        dict_=incoming
    )
    exp_settings.exp_duration_h = float(exp_settings.exp_duration_h)  # TODO: make more elegant
    exp_settings.interval = float(exp_settings.interval)  # TODO: make more elegant
    pico_params: PicoParams = utils.dataclass_from_dict(
        dataclass_=picoscope.PicoParams,
        dict_=incoming
    )
    thread = threading.Thread(
        target=Controller.start,
        args=(controller_, exp_settings, pico_params)
    )
    thread.start()
