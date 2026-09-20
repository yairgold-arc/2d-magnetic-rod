import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

from RodState import RodState
from plotRod import plotRod


class MagneticRod2D:
    """
    Planar magnetic rod.

    Initial implementation:
        - 2D
        - inextensible
        - static
        - magnetic domains
        - energy minimization

    Future:
        - field gradients
        - dipole interactions
        - dynamics
    """

    def __init__(
        self,
        length,      # [m]
        nseg,
        EI,          # [N m^2]
        area,        # [m^2]
        magnetization      # [A/m]
    ):

        # ==========================================
        # geometry
        # ==========================================

        self.length = float(length)
        self.nseg = int(nseg)

        self.ds = self.length / (self.nseg - 1)

        # ==========================================
        # boundary conditions
        # ==========================================

        self.x_base = 0.0
        self.y_base = 0.0
        self.theta_base = 0.0

        # ==========================================
        # material properties
        # stored per element
        # ==========================================

        self.EI = EI * np.ones(self.nseg - 1)

        # ==========================================
        # magnetic properties
        # stored per element
        # ==========================================

        self.area = area

        self.M = magnetization * np.ones(self.nseg - 1)

        # programmed magnetization angle
        # relative to local rod frame
        self.alpha0 = np.zeros(self.nseg - 1)

        # ==========================================
        # state
        # ==========================================

        self.state = RodState(self.nseg)

    # =====================================================
    # Plot
    # =====================================================

    def plot(
        self,
        field=None,
        theta_initial=None
    ):
        return plotRod(
            self,
            field=field,
            theta_initial=theta_initial
        )

    # =====================================================
    # Geometry
    # =====================================================

    def reconstruct_geometry(self):
        """
        Compute centerline coordinates
        from tangent angles.
        """

        theta = self.state.theta

        x = np.zeros(self.nseg)
        y = np.zeros(self.nseg)

        x[0] = self.x_base
        y[0] = self.y_base

        for i in range(self.nseg - 1):

            x[i + 1] = (
                x[i]
                + self.ds * np.cos(theta[i])
            )

            y[i + 1] = (
                y[i]
                + self.ds * np.sin(theta[i])
            )

        self.state.x = x
        self.state.y = y

    # =====================================================
    # Curvature
    # =====================================================

    def curvature(self):
        """
        Curvature evaluated on elements.
        """

        return (
            np.diff(self.state.theta)
            / self.ds
        )

    # =====================================================
    # Elastic Energy
    # =====================================================

    def elastic_energy(self):

        kappa = self.curvature()

        return (
            0.5
            * np.sum(
                self.EI
                * kappa**2
                * self.ds
            )
        )

    # =====================================================
    # Magnetic Energy
    # =====================================================

    def magnetic_energy(self, field):

        self.reconstruct_geometry()

        U = 0.0

        x = self.state.x
        y = self.state.y
        theta = self.state.theta

        for i in range(self.nseg - 1):

            # element center

            xc = 0.5 * (x[i] + x[i + 1])
            yc = 0.5 * (y[i] + y[i + 1])

            B = field.B(xc, yc)

            # ------------------------------------------------
            # CONSISTENT WITH reconstruct_geometry()
            #
            # Segment i orientation = theta[i]
            # ------------------------------------------------

            theta_elem = theta[i]

            # magnetization direction in lab frame

            phi = theta_elem + self.alpha0[i]

            mhat = np.array([
                np.cos(phi),
                np.sin(phi)
            ])

            U -= (
                self.area
                * self.M[i]
                * np.dot(mhat, B)
                * self.ds
            )

        return U

    # =====================================================
    # Total Energy
    # =====================================================

    def total_energy(self, field):

        return (
            self.elastic_energy()
            + self.magnetic_energy(field)
        )

    # =====================================================
    # Equilibrium
    # =====================================================

    def find_equilibrium(
        self,
        field,
        method="BFGS",
        tolerance=1e-9,
        max_iterations=1000,
        verbose=True
    ):
        """
        Find the static equilibrium configuration
        by minimizing total energy.
        """

        # Base clamped

        self.state.theta[0] = self.theta_base

        # Optimize all remaining angles

        theta_free_initial = self.state.theta[1:].copy()

        initial_energy = self.total_energy(field)

        def objective(theta_free):

            self.state.theta[0] = self.theta_base
            self.state.theta[1:] = theta_free

            return self.total_energy(field)

        result = minimize(
            objective,
            theta_free_initial,
            method=method,
            tol=tolerance,
            options={
                "maxiter": max_iterations,
                "disp": verbose
            }
        )

        if not result.success:
            raise RuntimeError(f"Equilibrium solve failed: {result.message}")

        self.state.theta[0] = self.theta_base
        self.state.theta[1:] = result.x

        # Store final solution

        self.state.theta[0] = self.theta_base
        self.state.theta[1:] = result.x

        self.reconstruct_geometry()

        final_energy = self.total_energy(field)

        if verbose:

            print()
            print("Equilibrium search")
            print("------------------")
            print(f"Success:             {result.success}")
            print(f"Message:             {result.message}")
            print(f"Iterations:          {result.nit}")
            print(f"Initial energy:      {initial_energy:.6e}")
            print(f"Final energy:        {final_energy:.6e}")
            print(
                "Energy reduction:   "
                f"{initial_energy - final_energy:.6e}"
            )

        return result
