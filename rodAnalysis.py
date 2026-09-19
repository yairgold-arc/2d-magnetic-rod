# rodAnalysis.py

import numpy as np
import matplotlib.pyplot as plt


def runFieldAngleScan(rod, field, B0, nAngles=72, theta_initial=None):

    if theta_initial is None:
        theta_initial = rod.state.theta.copy()

    fieldAngles = np.linspace(0, 2*np.pi, nAngles, endpoint=False)

    xtips, ytips, tipAngles = [], [], []

    for phi in fieldAngles:

        field.B0[:] = B0 * np.array([np.cos(phi), np.sin(phi)])
        rod.state.theta[:] = theta_initial

        rod.find_equilibrium(field, verbose=False)
        rod.reconstruct_geometry()

        xtips.append(rod.state.x[-1])
        ytips.append(rod.state.y[-1])

        dx = rod.state.x[-1] - rod.state.x[-2]
        dy = rod.state.y[-1] - rod.state.y[-2]

        tipAngles.append(np.rad2deg(np.arctan2(dy, dx)))

    return {
        "xtips": np.array(xtips),
        "ytips": np.array(ytips),
        "tipAngles": np.array(tipAngles),
        "fieldAngles": np.rad2deg(fieldAngles)
    }


def plotFieldAngleScan(results):

    xtips = results["xtips"]
    ytips = results["ytips"]
    tipAngles = results["tipAngles"]
    fieldAngles = results["fieldAngles"]

    fig, ax = plt.subplots(2, 2, figsize=(12, 10))

    sc = ax[0, 0].scatter(xtips, ytips, c=fieldAngles, cmap="hsv", s=80)

    ax[0, 0].plot(xtips, ytips, "k--", alpha=0.3)
    ax[0, 0].scatter(0, 0, c="k", s=120)
    ax[0, 0].axis("equal")
    ax[0, 0].grid(True)
    ax[0, 0].set_title("Reachable Tip Positions")
    ax[0, 0].set_xlabel("x [m]")
    ax[0, 0].set_ylabel("y [m]")

    fig.colorbar(sc, ax=ax[0, 0], label="Field Angle [deg]")

    ax[0, 1].plot(fieldAngles, tipAngles, "o-", linewidth=2)
    ax[0, 1].grid(True)
    ax[0, 1].set_title("Tip Angle vs Field Angle")
    ax[0, 1].set_xlabel("Field Angle [deg]")
    ax[0, 1].set_ylabel("Tip Angle [deg]")

    ax[1, 0].hist(tipAngles, bins=18, color="tab:blue", edgecolor="k")
    ax[1, 0].grid(True)
    ax[1, 0].set_title("Reachable Direction Histogram")
    ax[1, 0].set_xlabel("Tip Angle [deg]")
    ax[1, 0].set_ylabel("Count")

    tipRadius = np.sqrt(xtips**2 + ytips**2)

    ax[1, 1].plot(fieldAngles, tipRadius, "o-")
    ax[1, 1].grid(True)
    ax[1, 1].set_title("Tip Radius vs Field Angle")
    ax[1, 1].set_xlabel("Field Angle [deg]")
    ax[1, 1].set_ylabel("Radius [m]")

    plt.tight_layout()

    return fig, ax
