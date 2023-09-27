from dataclasses import dataclass
from enum import auto
from time import sleep, time
from typing import Dict

from aenum import Enum, unique

from remotecontrol import database, mux, picoscope, pulser, utils


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
    def __init__(self, mux: mux.Channel):
        self.mux_ = mux
        self._status = Status.not_started

    @property
    def status(self) -> int:
        return self._status.value

    @property
    def last_updated(self) -> str:
        pass

    def start(self, payload):
        self.parameters = payload
        self._status = Status.running
        
        self.database = database.Database(db_filename=self.parameters["exp_id"])
        self.database.write_metadata(self.parameters)
        # self.time_started = time()
        sleep(1)  # To ensure correct status message is returned

        return self.status

    def stop(self):
        self._status = Status.stopped

    def _acoustify(self, pulsing_params: Dict[str, float]) -> None:
        payload: Dict[str, float] = {'time': time()}
        waveforms: Dict[str, list[float]] = picoscope.callback(
            pulsing_params=pulsing_params
        )
        payload.update(waveforms)
        self.database.write(payload)


    def pulse(self):#, pulser_, picoscope_, mux_):
        mux.mux(channel=self.mux_)
        pulser.set_properties(self.parameters["pulser"])
        sleep(0.05)  # Needed! The time it takes the pulser to switch
        self._acoustify(pulsing_params=self.parameters["picoscope"])


@unique
class Switches(Enum):
    pikachu = 0
    zapdos = 1
    magnemite = 2
    jolteon = 3
    raichu = 4
    electabuzz = 5
    jigglypuff = 6
    voltorb = 7


jigs: Dict[str, Jig] = {
    'pickachu': Jig(mux=mux.Channel(Switches.pikachu)),
    'zapdos': Jig(mux=mux.Channel(Switches.zapdos)),
    'magnemite': Jig(mux=mux.Channel(Switches.magnemite)),    
    'jolteon': Jig(mux=mux.Channel(Switches.jolteon)),
    'raichu': Jig(mux=mux.Channel(Switches.raichu)),
    'electabuzz': Jig(mux=mux.Channel(Switches.electabuzz)),
    'jigglypuff': Jig(mux=mux.Channel(Switches.jigglypuff)),
    'voltorb': Jig(mux=mux.Channel(Switches.voltorb)),
}
