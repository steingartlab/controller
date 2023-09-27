"""Control acoustics experiments."""

from dataclasses import dataclass
from enum import auto
import logging
import threading
from time import sleep, time

from remotecontrol import jigs, logger


logger.configure()

SLEEP_BASELINE = 10


class Controller:
    def __init__(self):
        self.jigs = jigs.jigs

    def check_which_jigs_are_running(self):
        active_jigs = list()
        
        for jig in self.jigs:
            if jig.status != 1:
                continue

            active_jigs.append(jig)

        return active_jigs

    # def check_if_experiment_is_finished(self):
    #     for jig in self.jigs:


    def loop(self): #Add try except
        while True:
            # self.check_if_experiment_is_finished()
            active_jigs = self.check_which_jigs_are_running()
            sleep_duration_s = SLEEP_BASELINE / (len(active_jigs) + 1)

            for active_jig in active_jigs:
                jigs.Jig.pulse(active_jig)
                sleep(sleep_duration_s)
            
