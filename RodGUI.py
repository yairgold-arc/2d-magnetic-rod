from MagneticField2D import MagneticField2D
from MagneticRod2D import MagneticRod2D
from ToolTip import ToolTip

import tkinter as tk
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


matplotlib.use("TkAgg")


class RodGUI:

    def __init__(self, root):

        self.root = root

        root.title("Magnetic Rod")
        root.configure(padx=20, pady=20)

        label_font = ("Arial", 14)
        entry_font = ("Arial", 14)
        title_font = ("Arial", 16, "bold")
        button_font = ("Arial", 14, "bold")

        title = tk.Label(root, text="Rod Parameters", font=title_font)

        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        length_label = tk.Label(root, text="Length [m]", font=label_font)
        length_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        ToolTip(length_label, "Total rod length in meters.")

        self.length_var = tk.StringVar(value="0.1")
        tk.Entry(root, textvariable=self.length_var, font=entry_font,
                 justify="center", width=12).grid(row=1, column=1, padx=10, pady=5)

        nseg_label = tk.Label(root, text="Num. Seg.", font=label_font)
        nseg_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        ToolTip(nseg_label,
                "Number of rod segments.\nHigher values improve accuracy but increase solve time.")

        self.nseg_var = tk.StringVar(value="31")
        tk.Entry(root, textvariable=self.nseg_var, font=entry_font,
                 justify="center", width=12).grid(row=2, column=1, padx=10, pady=5)

        ei_label = tk.Label(root, text="E x I [N·m²]", font=label_font)
        ei_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        ToolTip(ei_label,
                "Rod bending stiffness.\nLarger values produce a stiffer rod.")

        self.ei_var = tk.StringVar(value="1e-6")
        tk.Entry(root, textvariable=self.ei_var, font=entry_font,
                 justify="center", width=12).grid(row=3, column=1, padx=10, pady=5)

        area_label = tk.Label(root, text="Area [m²]", font=label_font)
        area_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)
        ToolTip(area_label,
                "Cross-sectional area.\nUsed when calculating magnetic energy.")

        self.area_var = tk.StringVar(value="1e-6")
        tk.Entry(root, textvariable=self.area_var, font=entry_font,
                 justify="center", width=12).grid(row=4, column=1, padx=10, pady=5)

        mag_label = tk.Label(root, text="Magnetization [A/m]", font=label_font)
        mag_label.grid(row=5, column=0, sticky="w", padx=10, pady=5)
        ToolTip(mag_label,
                "Magnetization amplitude M.\nFor sinusoidal profiles this is the peak value.")

        self.mag_var = tk.StringVar(value="1e5")
        tk.Entry(root, textvariable=self.mag_var, font=entry_font,
                 justify="center", width=12).grid(row=5, column=1, padx=10, pady=5)

        field_title = tk.Label(root, text="External Field", font=title_font)
        field_title.grid(row=6, column=0, columnspan=2,
                         sticky="w", pady=(20, 15))

        bx_label = tk.Label(root, text="Bx [T]", font=label_font)
        bx_label.grid(row=7, column=0, sticky="w", padx=10, pady=5)
        ToolTip(bx_label,
                "Magnetic field X component in Tesla.")

        self.bx_var = tk.StringVar(value="0.01")
        tk.Entry(root, textvariable=self.bx_var, font=entry_font,
                 justify="center", width=12).grid(row=7, column=1, padx=10, pady=5)

        by_label = tk.Label(root, text="By [T]", font=label_font)
        by_label.grid(row=8, column=0, sticky="w", padx=10, pady=5)
        ToolTip(by_label,
                "Magnetic field Y component in Tesla.")

        self.by_var = tk.StringVar(value="0.01")
        tk.Entry(root, textvariable=self.by_var, font=entry_font,
                 justify="center", width=12).grid(row=8, column=1, padx=10, pady=5)

        tk.Label(root, text="Magnetization Profile", font=title_font).grid(
            row=9, column=0, columnspan=2, sticky="w", pady=(20, 15))

        self.profile_var = tk.StringVar(value="Fixed")
        tk.OptionMenu(root, self.profile_var, "Fixed", "Alternating", "Helix", 'Sinusoid').grid(
            row=10, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        self.profile_frame = tk.Frame(root)
        self.profile_frame.grid(row=11, column=0, columnspan=2, pady=10)

        self.profile_var.trace_add("write", self.update_profile_parameters)
        self.update_profile_parameters()

        tk.Button(root, text="Solve", font=button_font, bg="lightblue", width=15,
                  height=2, command=self.solve).grid(row=12, column=0, columnspan=2, pady=25)

    def update_profile_parameters(self, *args):

        for widget in self.profile_frame.winfo_children():
            widget.destroy()

        profile = self.profile_var.get()

        if profile == "Fixed":
            tk.Label(self.profile_frame, text="Angle [deg]").grid(
                row=0, column=0, padx=10, pady=5)

            self.angle_var = tk.StringVar(value="0")

            tk.Entry(self.profile_frame, textvariable=self.angle_var,
                     justify="center", width=12).grid(
                         row=0, column=1, padx=10, pady=5)

        elif profile == "Alternating":
            tk.Label(self.profile_frame, text="Amplitude [deg]").grid(
                row=0, column=0, padx=10, pady=5)

            self.alt_amp_var = tk.StringVar(value="90")

            tk.Entry(self.profile_frame, textvariable=self.alt_amp_var,
                     justify="center", width=12).grid(
                         row=0, column=1, padx=10, pady=5)

        elif profile == "Helix":
            tk.Label(self.profile_frame, text="Turns").grid(
                row=0, column=0, padx=10, pady=5)

            self.turns_var = tk.StringVar(value="4")

            tk.Entry(self.profile_frame, textvariable=self.turns_var,
                     justify="center", width=12).grid(
                         row=0, column=1, padx=10, pady=5)

        elif profile == "Sinusoid":

            tk.Label(self.profile_frame, text="Amplitude [deg]").grid(
                row=0, column=0, padx=10, pady=5)

            self.sin_amp_var = tk.StringVar(value="90")

            tk.Entry(self.profile_frame, textvariable=self.sin_amp_var,
                     justify="center", width=12).grid(
                row=0, column=1, padx=10, pady=5)

            tk.Label(self.profile_frame, text="Periods").grid(
                row=1, column=0, padx=10, pady=5)

            self.sin_waves_var = tk.StringVar(value="1")

            tk.Entry(self.profile_frame, textvariable=self.sin_waves_var,
                     justify="center", width=12).grid(
                row=1, column=1, padx=10, pady=5)

    def build_alpha(self, profile, nseg):

        if profile == "Fixed":
            angle = float(self.angle_var.get())
            return np.deg2rad(angle) * np.ones(nseg - 1)

        if profile == "Alternating":
            amp = float(self.alt_amp_var.get())
            return np.deg2rad(amp) * (1 - 2 * (np.arange(nseg - 1) % 2))

        if profile == "Helix":
            turns = float(self.turns_var.get())
            s = (np.arange(nseg - 1) + 0.5) / (nseg - 1)
            return turns * 2 * np.pi * s

        if profile == "Sinusoid":
            amp = float(self.sin_amp_var.get())
            waves = float(self.sin_waves_var.get())
            s = (np.arange(nseg - 1) + 0.5) / (nseg - 1)
            return np.deg2rad(amp) * np.sin(2 * np.pi * waves * s)

        return np.zeros(nseg - 1)

    def solve(self):

        length = float(self.length_var.get())
        nseg = int(self.nseg_var.get())
        ei = float(self.ei_var.get())
        area = float(self.area_var.get())
        magnetization = float(self.mag_var.get())

        bx = float(self.bx_var.get())
        by = float(self.by_var.get())

        profile = self.profile_var.get()

        rod = MagneticRod2D(length=length, nseg=nseg, EI=ei,
                            area=area, magnetization=magnetization)

        rod.alpha0[:] = self.build_alpha(profile, nseg)

        rod.M[:] = magnetization

        if profile == "Sinusoid":

            periods = float(self.sin_waves_var.get())

            s = (np.arange(nseg - 1) + 0.5)/(nseg - 1)

            rod.M[:] = magnetization * np.sin(2*np.pi*periods*s)

        field = MagneticField2D(B0=np.array([bx, by]))

        theta0 = rod.state.theta.copy()

        rod.find_equilibrium(field, verbose=False)

        rod.plot(field=field, theta_initial=theta0)

        plt.show()


if __name__ == "__main__":

    root = tk.Tk()
    app = RodGUI(root)
    root.mainloop()
