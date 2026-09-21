# rodAnalysis.py

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm


def runFieldAngleScan(
    rod, field, B0, nAngles=72, theta_initial=None, progress_callback=None
):

    if theta_initial is None:
        theta_initial = rod.state.theta.copy()

    theta_saved = rod.state.theta.copy()

    rod.state.theta[:] = theta_initial
    rod.reconstruct_geometry()

    xInitial = rod.state.x.copy()
    yInitial = rod.state.y.copy()

    rod.state.theta[:] = theta_saved

    fieldAngles = np.linspace(0, 2*np.pi, nAngles, endpoint=False)

    xtips, ytips, tipAngles = [], [], []
    UbendList, UmagList = [], []

    angles = fieldAngles if progress_callback is not None else tqdm(
        fieldAngles, desc="B0 Scan")

    for index, phi in enumerate(angles, start=1):

        field.B0[:] = B0 * np.array([
            np.cos(phi),
            np.sin(phi)
        ])

        rod.state.theta[:] = theta_initial

        rod.find_equilibrium(
            field,
            verbose=False
        )

        rod.reconstruct_geometry()

        # ---------------------------------
        # Tip position
        # ---------------------------------

        xtips.append(rod.state.x[-1])
        ytips.append(rod.state.y[-1])

        dx = rod.state.x[-1] - rod.state.x[-2]
        dy = rod.state.y[-1] - rod.state.y[-2]

        tipAngles.append(
            np.rad2deg(
                np.arctan2(dy, dx)
            )
        )

        # ---------------------------------
        # Bending energy
        # ---------------------------------

        ds = rod.length / (rod.nseg - 1)

        dtheta = np.diff(rod.state.theta)

        Ubend = (
            0.5
            * rod.EI[0]
            * np.sum((dtheta / ds)**2)
            * ds
        )

        # ---------------------------------
        # Magnetic energy
        # ---------------------------------

        phiField = np.arctan2(
            field.B0[1],
            field.B0[0]
        )

        phiMag = (
            rod.state.theta[:-1]
            + rod.alpha0
        )

        Bmag = np.linalg.norm(field.B0)

        Umag = -np.sum(
            rod.M
            * rod.area
            * ds
            * Bmag
            * np.cos(phiMag - phiField)
        )

        UbendList.append(Ubend)
        UmagList.append(Umag)

        if progress_callback is not None:
            progress_callback(index, nAngles)

    return {
        "xtips": np.array(xtips),
        "ytips": np.array(ytips),
        "tipAngles": np.array(tipAngles),
        "Ubend": np.array(UbendList),
        "Umag": np.array(UmagList),
        "fieldAngles": np.rad2deg(fieldAngles),
        "xInitial": xInitial,
        "yInitial": yInitial,
        "alpha0": rod.alpha0.copy(),
        "M": rod.M.copy(),
        "length": rod.length,
        "nseg": rod.nseg,
        "EI": rod.EI.copy(),
        "area": rod.area
    }


def plotFieldAngleScan(results):

    xtips = results["xtips"]
    ytips = results["ytips"]

    tipAngles = np.rad2deg(
        np.unwrap(
            np.deg2rad(results["tipAngles"])
        )
    )

    Ubend = results["Ubend"]
    Umag = results["Umag"]
    fieldAngles = results["fieldAngles"]

    xInitial = results["xInitial"]
    yInitial = results["yInitial"]
    alpha0 = results["alpha0"]
    M = results["M"]
    length = results["length"]
    nseg = results["nseg"]
    EI = results["EI"]
    area = results["area"]

    trackingError = tipAngles - fieldAngles

    fig, ax = plt.subplots(2, 2, figsize=(12, 10))

    # ==========================================================
    # Reachable Workspace
    # ==========================================================

    ax[0, 0].plot(
        xInitial,
        yInitial,
        "k-",
        lw=2,
        markersize=3,
        label="Initial Shape"
    )

    xc = 0.5 * (xInitial[0] + xInitial[1])
    yc = 0.5 * (yInitial[0] + yInitial[1])

    arrowScale = 0.01

    for i in range(len(alpha0)):

        xc = 0.5 * (xInitial[i] + xInitial[i+1])
        yc = 0.5 * (yInitial[i] + yInitial[i+1])

        mx = np.cos(alpha0[i])
        my = np.sin(alpha0[i])

        Mscale = M[i]
        if np.max(np.abs(M)) > 0:
            Mscale /= np.max(np.abs(M))

        ax[0, 0].arrow(
            xc,
            yc,
            arrowScale * Mscale * mx,
            arrowScale * Mscale * my,
            color="red",
            width=0.0002,
            head_width=0.003,
            head_length=0.004,
            length_includes_head=True,
            zorder=20
        )

    sc = ax[0, 0].scatter(
        xtips,
        ytips,
        c=fieldAngles,
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

    ax[0, 0].set_title("Reachable Workspace")
    ax[0, 0].set_xlabel("x [m]")
    ax[0, 0].set_ylabel("y [m]")

    ax[0, 0].legend()

    fig.colorbar(
        sc,
        ax=ax[0, 0],
        label="Field Angle [deg]"
    )

    # ==========================================================
    # Tip Angle vs Field Angle
    # ==========================================================

    ax[0, 1].plot(
        fieldAngles,
        tipAngles,
        "o-",
        lw=2,
        label="Tip"
    )

    ax[0, 1].grid(True)

    ax[0, 1].set_title("Tip Angle vs Field Angle")
    ax[0, 1].set_xlabel("Field Angle [deg]")
    ax[0, 1].set_ylabel("Tip Angle [deg]")

    # ==========================================================
    # Reachable Direction Histogram
    # ==========================================================

    bins = np.arange(-180, 181, 5)

    ax[1, 0].hist(
        tipAngles,
        bins=bins,
        color="tab:blue",
        edgecolor="k"
    )

    ax[1, 0].grid(True)

    ax[1, 0].set_title("Reachable Direction Histogram")
    ax[1, 0].set_xlabel("Tip Angle [deg]")
    ax[1, 0].set_ylabel("Count")
    ax[1, 0].set_xlim(-180, 180)
    ax[1, 0].set_xticks(np.arange(-180, 181, 20))

    # ==========================================================
    # Energies
    # ==========================================================

    ax[1, 1].plot(
        fieldAngles,
        Ubend,
        "o-",
        lw=2,
        label="Bending"
    )

    ax[1, 1].plot(
        fieldAngles,
        Umag,
        "s-",
        lw=2,
        label="Magnetic")

    ax[1, 1].grid(True)
    ax[1, 1].set_title("Energy")
    ax[1, 1].set_xlabel("Field Angle [deg]")
    ax[1, 1].set_ylabel("Energy [J]")
    ax[1, 1].legend()

    return fig, ax
