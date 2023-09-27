"""Control acoustics experiments."""

from time import sleep
from typing import Dict

from remotecontrol import jigs, logger


logger.configure()

SLEEP_BASELINE = 10


class Controller:
    def __init__(self):
        self.jigs = jigs.jigs

    def check_which_jigs_are_running(self) -> Dict[str, jigs.Jig]:
        active_jigs = dict()
        
        for name, jig in self.jigs.items():
            if jig.status != jigs.Status.running.value:
                continue

            active_jigs[name] = jigg

        return active_jigs

    # def check_if_experiment_is_finished(self):
    #     for jig in self.jigs:


    def loop(self): #Add try except
        while True:
            active_jigs = self.check_which_jigs_are_running()

            if len(active_jigs) == 0:
                sleep(1)
                continue

            sleep_duration_s = SLEEP_BASELINE / (len(active_jigs) + 1)

            for active_jig in active_jigs.values():
                jigs.Jig.pulse(active_jig)
                sleep(sleep_duration_s)
            
