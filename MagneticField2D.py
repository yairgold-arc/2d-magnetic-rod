import numpy as np


class MagneticField2D:

    def __init__(
        self,
        B0=np.zeros(2),
        G=np.zeros((2, 2))
    ):
        """
        B(x) = B0 + G r

        B0 : uniform field vector [T]
        G  : field gradient tensor [T/m]
        """
        self.B0 = np.asarray(B0, dtype=float)
        self.G = np.asarray(G, dtype=float)

    def B(self, x, y):

        r = np.array([x, y])

        return self.B0 + self.G @ r
