import numpy as np
import matplotlib.pyplot as plt

from MagneticRod2D import MagneticRod2D
from MagneticField2D import MagneticField2D

# Create rod
rod = MagneticRod2D(
    length=0.1,
    nseg=21,
    EI=1e-6,
    area=1e-6,
    magnetization=1e5
)

# Create magnetic field
field = MagneticField2D(
    B0=np.array([0.01, 0.01])
)

# Store initial state
theta0 = rod.state.theta.copy()

# Solve equilibrium
rod.find_equilibrium(field)

# Plot
rod.plot(
    field=field,
    theta_initial=theta0
)

plt.show()
