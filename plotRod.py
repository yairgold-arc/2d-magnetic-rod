import matplotlib.pyplot as plt
import numpy as np


def plotRod(self, field=None, theta_initial=None):

    self.reconstruct_geometry()

    x = self.state.x.copy()
    y = self.state.y.copy()
    theta = self.state.theta.copy()

    x0 = None
    y0 = None

    if theta_initial is not None:
        theta_saved = self.state.theta.copy()
        self.state.theta[:] = theta_initial
        self.reconstruct_geometry()
        x0 = self.state.x.copy()
        y0 = self.state.y.copy()
        self.state.theta[:] = theta_saved
        self.reconstruct_geometry()

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.subplots_adjust(right=0.72)

    if x0 is not None:

        ax.plot(x0, y0, '--', color='gray', linewidth=2, label='Initial')
        ax.scatter(x0, y0, s=20, c='gray', zorder=5)

        for i in range(self.nseg - 1):

            xc = 0.5 * (x0[i] + x0[i + 1])
            yc = 0.5 * (y0[i] + y0[i + 1])

            phi = theta_initial[i] + self.alpha0[i]
            mx = np.cos(phi)
            my = np.sin(phi)

            ax.arrow(xc, yc,
                     0.10 * self.length * mx,
                     0.10 * self.length * my,
                     color='lightcoral',
                     alpha=0.6,
                     width=0.0003 * self.length,
                     head_width=0.008 * self.length,
                     head_length=0.015 * self.length,
                     length_includes_head=True,
                     zorder=15)

    ax.plot(x, y, 'k-', linewidth=3,
            label='Final' if theta_initial is not None else 'Rod')
    ax.scatter(x, y, s=30, c='black', zorder=20)

    scale = 0.12 * self.length

    for i in range(self.nseg - 1):

        xc = 0.5 * (x[i] + x[i + 1])
        yc = 0.5 * (y[i] + y[i + 1])

        phi = theta[i] + self.alpha0[i]
        mx = np.cos(phi)
        my = np.sin(phi)

        ax.arrow(xc, yc,
                 scale * mx,
                 scale * my,
                 color='red',
                 width=0.0006 * self.length,
                 head_width=0.010 * self.length,
                 head_length=0.020 * self.length,
                 length_includes_head=True,
                 zorder=30)

    if field is not None:

        B = field.B(0.0, 0.0)
        Bnorm = np.linalg.norm(B)

        if Bnorm > 0:

            Bhat = B / Bnorm
            x_field = np.max(x) + 0.15 * self.length
            y_field = np.max(y)

            ax.arrow(x_field, y_field,
                     0.20 * self.length * Bhat[0],
                     0.20 * self.length * Bhat[1],
                     color='blue',
                     width=0.001 * self.length,
                     head_width=0.015 * self.length,
                     head_length=0.03 * self.length,
                     length_includes_head=True,
                     zorder=40)

            ax.text(x_field,
                    y_field + 0.04 * self.length,
                    'B',
                    color='blue',
                    fontsize=14,
                    fontweight='bold')

    info = (
        f"L      = {self.length:.3g} m\n"
        f"NSEG   = {self.nseg}\n"
        f"EI     = {self.EI[0]:.2e} N·m²\n"
        f"Area   = {self.area:.2e} m²\n"
        f"M      = {self.M[0]:.2e} A/m"
    )

    if field is not None:
        info += (
            f"\nBx     = {field.B0[0]:.3f} T"
            f"\nBy     = {field.B0[1]:.3f} T"
        )

    fig.text(0.75, 0.90,
             info,
             ha='left',
             va='top',
             fontsize=10,
             family='monospace',
             bbox=dict(facecolor='white',
                       edgecolor='black',
                       alpha=0.9))

    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    min_y_span = 0.5 * self.length
    y_center = 0.5 * (ymin + ymax)

    if (ymax - ymin) < min_y_span:
        ymin = y_center - min_y_span / 2
        ymax = y_center + min_y_span / 2
    ax.set_ylim(ymin, ymax)

    ax.set_aspect('equal')
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.grid(True)
    ax.legend()

    return fig, ax
