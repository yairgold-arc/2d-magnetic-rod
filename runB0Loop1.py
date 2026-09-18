import matplotlib.pyplot as plt
from MagneticField2D import MagneticField2D
from MagneticRod2D import MagneticRod2D

import numpy as np
import matplotlib
matplotlib.use("TkAgg")


# ============================================================
# USER SETTINGS
# ============================================================

LENGTH = 0.1
NSEG = 31

EI = 1e-7
AREA = 1e-6
MAGNETIZATION = 1e5

B_MAGNITUDE = 0.01

N_FIELD_ANGLES = 72

FIELD_ANGLES = np.linspace(
    0,
    2*np.pi,
    N_FIELD_ANGLES,
    endpoint=False
)

# ============================================================
# INITIAL CONFIGURATION
# ============================================================

theta0 = 0
k = np.pi*NSEG

s = np.linspace(
    0.0,
    1.0,
    NSEG - 1
)

# alpha = theta0 + k*s
alpha = np.pi/2 * (1 - 2 * (np.arange(NSEG - 1) % 2))
theta_initial = np.zeros(NSEG)

# programmed magnetization profile

# examples

# alpha = np.deg2rad([0,0,0,0])
# alpha = np.deg2rad([0,30,60,90])
# alpha = np.deg2rad([0,90,180,270])

# ============================================================
# CREATE OBJECTS
# ============================================================

rod = MagneticRod2D(
    length=LENGTH,
    nseg=NSEG,
    EI=EI,
    area=AREA,
    magnetization=MAGNETIZATION
)

field = MagneticField2D(
    B0=np.array([B_MAGNITUDE, 0.0]),
    G=np.zeros((2, 2))
)

rod.alpha0[:] = alpha

# ============================================================
# STORAGE
# ============================================================

xtips = []
ytips = []
tip_angles = []

# ============================================================
# COMPUTE WORKSPACE
# ============================================================

for phi in FIELD_ANGLES:

    field.B0[:] = B_MAGNITUDE * np.array(
        [
            np.cos(phi),
            np.sin(phi)
        ]
    )

    print("Field angle [deg]:", np.rad2deg(phi))

    # Always restart from same reference state

    rod.state.theta[:] = theta_initial

    rod.find_equilibrium(
        field,
        verbose=False
    )

    rod.reconstruct_geometry()

    xtips.append(
        rod.state.x[-1]
    )

    ytips.append(
        rod.state.y[-1]
    )

    # Tip segment orientation

    dx = (
        rod.state.x[-1]
        - rod.state.x[-2]
    )

    dy = (
        rod.state.y[-1]
        - rod.state.y[-2]
    )

    tip_angle = np.rad2deg(
        np.arctan2(dy, dx)
    )

    tip_angles.append(
        tip_angle
    )

# ============================================================
# CONVERT
# ============================================================

xtips = np.array(xtips)
ytips = np.array(ytips)

tip_angles = np.array(
    tip_angles
)

field_angles_deg = np.rad2deg(
    FIELD_ANGLES
)

# ============================================================
# EXAMPLE EQUILIBRIUM
# B = 0 DEG
# ============================================================

field.B0[:] = B_MAGNITUDE * np.array(
    [1.0, 0.0]
)

rod.state.theta[:] = theta_initial

theta0 = rod.state.theta.copy()

rod.find_equilibrium(
    field,
    verbose=False
)

fig1, ax1 = rod.plot(
    field=field,
    theta_initial=theta0
)

# ============================================================
# FIGURE 2
# WORKSPACE RESULTS
# ============================================================

fig, ax = plt.subplots(
    2,
    2,
    figsize=(12, 10)
)

# ------------------------------------------------------------
# Reachable tip positions
# ------------------------------------------------------------

sc = ax[0, 0].scatter(
    xtips,
    ytips,
    c=field_angles_deg,
    cmap="hsv",
    s=80
)

ax[0, 0].plot(
    xtips,
    ytips,
    "k--",
    alpha=0.3
)

ax[0, 0].scatter(
    0,
    0,
    c="k",
    s=120
)

ax[0, 0].axis("equal")
ax[0, 0].grid(True)

ax[0, 0].set_title(
    "Reachable Tip Positions"
)

ax[0, 0].set_xlabel("x [m]")
ax[0, 0].set_ylabel("y [m]")

fig.colorbar(
    sc,
    ax=ax[0, 0],
    label="Field Angle [deg]"
)

# ------------------------------------------------------------
# Tip response
# ------------------------------------------------------------

ax[0, 1].plot(
    field_angles_deg,
    tip_angles,
    "o-",
    linewidth=2
)

ax[0, 1].grid(True)

ax[0, 1].set_title(
    "Tip Angle vs Field Angle"
)

ax[0, 1].set_xlabel(
    "Field Angle [deg]"
)

ax[0, 1].set_ylabel(
    "Tip Angle [deg]"
)

# ------------------------------------------------------------
# Histogram
# ------------------------------------------------------------

ax[1, 0].hist(
    tip_angles,
    bins=18,
    color="tab:blue",
    edgecolor="k"
)

ax[1, 0].grid(True)

ax[1, 0].set_title(
    "Reachable Direction Histogram"
)

ax[1, 0].set_xlabel(
    "Tip Angle [deg]"
)

ax[1, 0].set_ylabel(
    "Count"
)

# ------------------------------------------------------------
# Magnetization profile
# ------------------------------------------------------------

tip_radius = np.sqrt(
    xtips**2 +
    ytips**2
)

ax[1, 1].plot(
    field_angles_deg,
    tip_radius,
    'o-'
)

ax[1, 1].set_title(
    'Tip Radius vs Field Angle'
)

ax[1, 1].set_xlabel(
    'Field Angle [deg]'
)

ax[1, 1].set_ylabel(
    'Radius [m]'
)

ax[1, 1].grid(True)


plt.tight_layout()
plt.show()
