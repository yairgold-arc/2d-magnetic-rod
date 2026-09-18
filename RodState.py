import numpy as np


class RodState:

    def __init__(self, nseg):

        self.theta = np.zeros(nseg)

        # reconstructed geometry
        self.x = np.zeros(nseg)
        self.y = np.zeros(nseg)

        # future dynamics
        self.omega = np.zeros(nseg)

        self.time = 0.0
