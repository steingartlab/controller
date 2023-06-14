# controller

Controlling experiments is one thing, but perhaps more importantly it monitors whether an experiment is being run on the computer, i.e. it is not bound to an experiment being controlled by the controller (it is admittedly done rather crudely, but this is not written for mass-market adoption anyway). This means that this is still useful for maintaining central oversight over all acoustics experiments being run, even though the user may be running a customized experiment where this `controller` isn't applicable, e.g. 2D acoustics or multiplexing.

Furthermore, this means that we don't have to maintain N instances of pithy, which can be quite the pain when we want to update control scripts. This makes control more structured