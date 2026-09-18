import matplotlib.pyplot as plt
import numpy as np

from MagneticRod2D import MagneticRod2D
from MagneticField2D import MagneticField2D

import matplotlib
matplotlib.use("TkAgg")


# =====================================================
# Create rod
# =====================================================

rod = MagneticRod2D(
    length=3,
    nseg=41,
    EI=1e-2,
    area=1e-6,
    magnetization=1e5
)

# =====================================================
# Initial state
# =====================================================

# straight horizontal rod

rod.state.theta[:] = 0.0

# random magnetization direction in each segment's local frame

# rng = np.random.default_rng()
# rod.alpha0[:] = rng.uniform(0.0, 2.0 * np.pi, size=rod.nseg - 1)

NSEG = rod.nseg

theta0 = 0
k = 2*np.pi*NSEG
s = np.linspace(0.0, 1.0, NSEG - 1)
alpha = theta0 + k*s

# alpha = np.pi/2 * (1 - 2 * (np.arange(NSEG - 1) % 2))
rod.alpha0[:] = alpha  # np.pi/2  # np.zeros(NSEG)

# =====================================================
# Uniform vertical field
# =====================================================

field = MagneticField2D(
    B0=np.array([-0.2, 0.1]),  # +Y direction
    G=np.zeros((2, 2))
)

# =====================================================
# Initial energy
# =====================================================

U0 = rod.total_energy(field)

print()
print("Initial energy")
print("--------------")
print(U0)

# =====================================================
# Save initial configuration
# =====================================================

theta0 = rod.state.theta.copy()

# =====================================================
# Solve equilibrium
# =====================================================

result = rod.find_equilibrium(field)

# =====================================================
# Final energy
# =====================================================

Uf = rod.total_energy(field)

print()
print("Final energy")
print("------------")
print(Uf)

print()
print("Energy reduction")
print("----------------")
print(U0 - Uf)

print()
print("Final theta [deg]")
print("-----------------")
print(
    np.round(
        np.rad2deg(rod.state.theta),
        2
    )
)

# =====================================================
# Plot comparison
# =====================================================

rod.plot(
    field=field,
    theta_initial=theta0
)

Bmag = np.linalg.norm(field.B0)

print("\n" + "="*55)
print("ROD CONFIGURATION")
print("="*55)
print(f"{'Length':25s}: {rod.length:.3f} m")
print(f"{'Segments':25s}: {rod.nseg}")
print(f"{'EI':25s}: {rod.EI[0]:.2e}")
print(f"{'Magnetization':25s}: {rod.M[0]:.2e} A/m")
print(f"{'Field B0':25s}: [{field.B0[0]:.3f}, {field.B0[1]:.3f}] T")
print(f"{'|B0|':25s}: {Bmag:.3f} T")
print(f"{'Initial rod angle':25s}: 0 deg")
print(f"{'Programmed twist k':25s}: {k/(2*np.pi):.1f} turns")
print(f"{'Alpha range':25s}: "
      f"{np.rad2deg(alpha.min()):.1f}° -> "
      f"{np.rad2deg(alpha.max()):.1f}°")
print("="*55)

plt.show()

# =====================================================
# Presentation summary
# =====================================================
