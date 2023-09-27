from dataclasses import dataclass
from time import sleep, time
from typing import Dict

from remotecontrol import database, jigs, logger, mux, picoscope, pulser, utils



@dataclass
class Mux:
    module: int
    switch: int


class Status(utils.ZeroBasedAutoEnum):
    """Experiment status. Passed to end user."""

    not_started = auto()
    running = auto()
    stopped = auto()
    error = auto()


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


class Jig:
    def __init__(self, mux: Mux):
        self.mux_ = mux
        self._status = Status.not_started

    @property
    def status(self) -> str:
        return str(self._status)

    @property
    def last_updated(self) -> str:
        pass

    def start(self, payload):
        self.parameters = payload
        self._status = Status.running
        sleep(1)  # To ensure correct status message is returned

        # self.time_started = time()

        return self.status

    def stop(self, status):
        self._status = status

    def _acoustify(self, pulsing_params: picoscope.Picoscope) -> None:
        payload: Dict[str, list[float]] = picoscope.callback(
            pulsing_params=pulsing_params
        )
        self.database.write(payload)


    def pulse(self, pulser_, picoscope_, mux_):
        mux.mux(channel=mux_)
        pulser.set_properties(pulser_)
        sleep(0.05)  # Needed! The time it takes the pulser to switch
        _acoustify(pulsing_params=mode.picoscope)          


jigs: Dict[str, Jig] = {
    'pickachu': Jig(mux=Mux(0, 0)),
    'zapdos': Jig(mux=Mux(0, 0)),
    'magnemite': Jig(mux=Mux(0, 0)),
    'jolteon': Jig(mux=Mux(0, 0)),
    'raichu': Jig(mux=Mux(0, 0)),
    'electabuzz': Jig(mux=Mux(0, 0)),
    'jigglypuff': Jig(mux=Mux(0, 0)),
    'voltorb': Jig(mux=Mux(0, 0)),
}
