"""Control acoustics experiments."""

from dataclasses import dataclass
from enum import auto
import logging
import threading
from time import sleep, time

from controller import database, logger, picoscope, pulser, utils


logger.configure()


@dataclass
class ExpSettings:
    """Experiment metadata.
    
    Note that this is separate from any pulsing parameters.

    Attributes:
        exp_duration_h (float): Duration of experiment [h].
        interval (float): Time passed between acoustic pulses [s].
        exp_id (str): (Preferably unique) experiment identifier.
    """

    exp_duration_h: float  # h
    interval: float  # s
    exp_id: str

    def __post_init__(self):
        """Ensure correct typing.
        
        All values in json objects received as a post request are automatically
        parsed as strings. We cannot have that here—this implicit method
        ensures correct conversion.
        
        Normally one would parse it before (data)class initialization, but for
        this case post init is a better solution as we have mixed instance types
        (float and str).
        """

        self.exp_duration_h = float(self.exp_duration_h)
        self.interval = float(self.interval)

    @property
    def exp_duration_s(self) -> float:
        """We need it in seconds while running, but the GUI wants it in hours.
        This is a quasi-elegant solution (or not).

        Returns:
            float: Experiment duration in seconds.
        """

        return self.exp_duration_h * 3600


class Status(utils.ZeroBasedAutoEnum):
    """Experiment status. Passed to end user."""

    not_started = auto()
    running = auto()
    stopped = auto()
    error = auto()


class Controller:
    """Stateful implementation of experimental control.

    It may be responsible for 

    Note that stop() is the only method called "externally", i.e. directly from
    the server. All other methods are called from wrappers.

    Attributes:
        start (float): The timestamp when the experiment started.
        pill (threading.Event): Event object used to control the experiment loop.
            Can be called externally to kill experiment.
        _status (Status): Object representing the current experiment status.
            See Status.

    """
    def __init__(self):
        self.start = None
        self._status = Status(0)
        self._flush_pill()
    
    @property
    def status(self) -> int:
        """Experiment status.

        Returns:
            int: The current experiment status as an integer. See class Status for possible values.
        """
        return self._status.value

    @status.setter
    def status(self, num):
        """Set the experiment status.

        Args:
            num (int): The new experiment status as an integer.

        """
        self._status = Status(num)

    @property
    def last_updated(self) -> int:
        """Get the timestamp of the last update in the data directory

        Returns:
            int: The timestamp of the last update.

        """
        return utils.last_folder_update()

    @property
    def time_elapsed(self) -> float:
        """Get the elapsed time since the start of the experiment.

        Returns:
            float: The elapsed time in seconds.

        """
        
        if self.start is None:
            return None
        
        return time() - self.start

    def _flush_pill(self):
        self.pill = threading.Event()

    def _loop(self, exp_settings: ExpSettings, pico_params: picoscope.PicoParams):
        """Internal loop for running the experiment.

        This method is the internal loop that runs the experiment until the specified duration is reached
        or until the experiment is manually stopped. It captures waveforms, saves the data, and updates
        the experiment status.

        Args:
            exp_settings (ExpSettings): The settings for the experiment.
            pico_params (picoscope.PicoParams): The parameters for the picoscope.
        """

        while self.time_elapsed < exp_settings.exp_duration_s and not self.pill.wait(exp_settings.interval):
            try:
                waveform: dict[str, list[float]] = _pulse(pico_params=pico_params)
                row_id = database.save(waveform=waveform, database_=self.database_)
                logging.info(f'Pulse completed. Row id: {row_id}')
                self.status = 1

            except Exception as e:
                logging.error(e)
                self.status = 3
                sleep(10)

    def _reset_start_time(self):
        self.start = time()

    def _start(self, exp_settings: ExpSettings, pico_params: picoscope.PicoParams) -> None: 
        """Start the experiment. Should be called as a thread.

        Args:
            exp_settings (ExpSettings): The settings for the experiment.
            pico_params (picoscope.PicoParams): The parameters for the picoscope.
        """

        self._reset_start_time()
        self.database_: database.Database = database.Database(db_filename=exp_settings.exp_id)    
        self.status = 1
        self._loop(exp_settings=exp_settings, pico_params=pico_params)
        self.status = 2

    def stop(self):
        """Manually stop experiment."""

        self.pill.set()
        self.pill = self._flush_pill()
        self.status = 2


def _pulse(pico_params: picoscope.PicoParams) -> dict[str, list[float]]:
    """Perform a pulse operation and return the waveform.

    Args:
        pico_params (picoscope.PicoParams): The parameters for the pulse operation.

    Returns:
        dict[str, list[float]]: The waveform data as a dictionary.
    """

    pulser.turn_on()
    waveform: dict[str, list[float]] = picoscope.callback(pico_params)
    pulser.turn_off()

    return waveform


def pulse(incoming: dict[str, str]) -> dict[str, list[float]]:
    """Pulsing wrapper.

    Is only utilized when performing a standalone pulse for data quality
    verification, i.e. not when experiment is run.

    Args:
        incoming (dict[str, str]): The incoming parameters for the pulse operation.

    Returns:
        dict[str, list[float]]: The waveform data as a dictionary.
    """

    pico_params: picoscope.PicoParams = utils.dataclass_from_dict(
        dataclass_=picoscope.PicoParams,
        dict_=incoming
    )

    return _pulse(pico_params)


def start_thread(controller_: Controller, incoming: dict[str, str]) -> None:
    """Wrapper for starting experiment as a thread.

    Args:
        controller_ (Controller): The controller object.
        incoming (dict[str, str]): The incoming parameters.

    Returns:
        None
    """

    exp_settings: ExpSettings = utils.dataclass_from_dict(
        dataclass_=ExpSettings,
        dict_=incoming
    )
    pico_params: picoscope.PicoParams = utils.dataclass_from_dict(
        dataclass_=picoscope.PicoParams,
        dict_=incoming
    )
    thread = threading.Thread(
        target=Controller._start,
        args=(controller_, exp_settings, pico_params)
    )
    thread.start()
