from tkinter import messagebox

from MagneticField2D import MagneticField2D
from MagneticRod2D import MagneticRod2D
from ToolTip import ToolTip
from rodAnalysis import runFieldAngleScan, plotFieldAngleScan

import tkinter as tk
from tkinter import ttk
import queue
import threading
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("TkAgg")


class RodGUI:

    def __init__(self, root):

        self.root = root

        root.title("2D Magnetic Rod simulator")
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
        ToolTip(nseg_label, "Number of rod segments.")

        self.nseg_var = tk.StringVar(value="11")
        tk.Entry(root, textvariable=self.nseg_var, font=entry_font,
                 justify="center", width=12).grid(row=2, column=1, padx=10, pady=5)

        ei_label = tk.Label(root, text="E x I [N·m²]", font=label_font)
        ei_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        ToolTip(ei_label,
                "Rod bending stiffness.\nE - Young's modulus, I - second moment of area.")

        self.ei_var = tk.StringVar(value="1e-6")
        tk.Entry(root, textvariable=self.ei_var, font=entry_font,
                 justify="center", width=12).grid(row=3, column=1, padx=10, pady=5)

        area_label = tk.Label(root, text="Area [m²]", font=label_font)
        area_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)
        ToolTip(area_label,
                "Cross-sectional area of the rod")

        self.area_var = tk.StringVar(value="1e-6")
        tk.Entry(root, textvariable=self.area_var, font=entry_font,
                 justify="center", width=12).grid(row=4, column=1, padx=10, pady=5)

        mag_label = tk.Label(root, text="Magnetization [A/m]", font=label_font)
        mag_label.grid(row=5, column=0, sticky="w", padx=10, pady=5)
        ToolTip(mag_label,
                "Magnetization amplitude M.")

        self.mag_var = tk.StringVar(value="1e5")
        tk.Entry(root, textvariable=self.mag_var, font=entry_font,
                 justify="center", width=12).grid(row=5, column=1, padx=10, pady=5)

        field_title = tk.Label(root, text="External Field", font=title_font)
        field_title.grid(row=6, column=0, columnspan=2,
                         sticky="w", pady=(20, 15))

        bx_label = tk.Label(root, text="Bx [T]", font=label_font)
        bx_label.grid(row=7, column=0, sticky="w", padx=10, pady=5)
        ToolTip(bx_label,
                "Magnetic field x-dir.")

        self.bx_var = tk.StringVar(value="0.01")
        tk.Entry(root, textvariable=self.bx_var, font=entry_font,
                 justify="center", width=12).grid(row=7, column=1, padx=10, pady=5)

        by_label = tk.Label(root, text="By [T]", font=label_font)
        by_label.grid(row=8, column=0, sticky="w", padx=10, pady=5)
        ToolTip(by_label,
                "Magnetic field y-dir.")

        self.by_var = tk.StringVar(value="0.01")
        tk.Entry(root, textvariable=self.by_var, font=entry_font,
                 justify="center", width=12).grid(row=8, column=1, padx=10, pady=5)

        tk.Label(root, text="Magnetization Profile", font=title_font).grid(
            row=9, column=0, columnspan=2, sticky="w", pady=(20, 15))

        self.profile_var = tk.StringVar(value="Fixed")
        profile_menu = tk.OptionMenu(
            root, self.profile_var, "Fixed", "Alternating", "Helix", "Sinusoid")
        profile_menu.config(font=entry_font)
        profile_menu["menu"].config(font=entry_font)
        profile_menu.grid(
            row=10, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        self.profile_frame = tk.Frame(root)
        self.profile_frame.grid(row=11, column=0, columnspan=2, pady=10)

        self.profile_var.trace_add("write", self.update_profile_parameters)
        self.update_profile_parameters()

        tk.Button(root, text="Equilibrium config.", font=button_font, bg="lightblue", width=16,
                  height=2, command=self.solve).grid(row=12, column=0, columnspan=2, pady=10)

        tk.Button(root, text="B0 Scan", font=button_font, bg="lightblue", width=16,
                  height=2, command=self.runB0Scan).grid(row=13, column=0, columnspan=2, pady=10)

    def update_profile_parameters(self, *args):

        profile_label_font = ("Arial", 14)
        profile_entry_font = ("Arial", 14)

        for widget in self.profile_frame.winfo_children():
            widget.destroy()

        profile = self.profile_var.get()

        if profile == "Fixed":
            tk.Label(self.profile_frame, text="Angle [deg]",
                     font=profile_label_font).grid(
                row=0, column=0, padx=10, pady=5)

            self.angle_var = tk.StringVar(value="0")

            tk.Entry(self.profile_frame, textvariable=self.angle_var,
                     font=profile_entry_font,
                     justify="center", width=12).grid(
                         row=0, column=1, padx=10, pady=5)

        elif profile == "Alternating":
            tk.Label(self.profile_frame, text="Amplitude [deg]",
                     font=profile_label_font).grid(
                row=0, column=0, padx=10, pady=5)

            self.alt_amp_var = tk.StringVar(value="90")

            tk.Entry(self.profile_frame, textvariable=self.alt_amp_var,
                     font=profile_entry_font,
                     justify="center", width=12).grid(
                         row=0, column=1, padx=10, pady=5)

        elif profile == "Helix":
            tk.Label(self.profile_frame, text="Turns",
                     font=profile_label_font).grid(
                row=0, column=0, padx=10, pady=5)

            self.turns_var = tk.StringVar(value="4")

            tk.Entry(self.profile_frame, textvariable=self.turns_var,
                     font=profile_entry_font,
                     justify="center", width=12).grid(
                         row=0, column=1, padx=10, pady=5)

        elif profile == "Sinusoid":

            tk.Label(self.profile_frame, text="Amplitude [deg]",
                     font=profile_label_font).grid(
                row=0, column=0, padx=10, pady=5)

            self.sin_amp_var = tk.StringVar(value="90")

            tk.Entry(self.profile_frame, textvariable=self.sin_amp_var,
                     font=profile_entry_font,
                     justify="center", width=12).grid(
                row=0, column=1, padx=10, pady=5)

            tk.Label(self.profile_frame, text="Periods",
                     font=profile_label_font).grid(
                row=1, column=0, padx=10, pady=5)

            self.sin_waves_var = tk.StringVar(value="1")

            tk.Entry(self.profile_frame, textvariable=self.sin_waves_var,
                     font=profile_entry_font,
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
        try:
            length = float(self.length_var.get())
            nseg = int(self.nseg_var.get())
            ei = float(self.ei_var.get())
            area = float(self.area_var.get())
            magnetization = float(self.mag_var.get())
            bx = float(self.bx_var.get())
            by = float(self.by_var.get())

            if length <= 0:
                raise ValueError("Length must be positive.")

            if nseg < 3:
                raise ValueError("Number of segments must be at least 3.")

            if ei <= 0:
                raise ValueError("EI must be positive.")

            if area <= 0:
                raise ValueError("Area must be positive.")

        except Exception as e:
            messagebox.showerror("Invalid Input", str(e))
            return

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

    def runB0Scan(self):

        progressWin = tk.Toplevel(self.root)
        progressWin.title("B0 Scan")
        progressWin.geometry("300x80")

        tk.Label(progressWin, text="Running B0 field angle scan...").pack(pady=5)

        progressBar = ttk.Progressbar(
            progressWin, length=250, mode="determinate")
        progressBar.pack(pady=5)

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

        if profile == "Sinusoid":
            periods = float(self.sin_waves_var.get())
            s = (np.arange(nseg - 1) + 0.5) / (nseg - 1)
            rod.M[:] = magnetization * np.sin(2 * np.pi * periods * s)

        field = MagneticField2D(B0=np.array([bx, by]))
        theta_initial = rod.state.theta.copy()

        progressBar.configure(maximum=72, value=0)
        progress_queue = queue.Queue()

        def run_scan():
            try:
                results = runFieldAngleScan(
                    rod,
                    field,
                    B0=float(np.hypot(bx, by)),
                    theta_initial=theta_initial,
                    progress_callback=lambda current, total: progress_queue.put(
                        ("progress", current, total)
                    )
                )
                progress_queue.put(("done", results))
            except Exception as error:
                progress_queue.put(("error", error))

        threading.Thread(target=run_scan, daemon=True).start()
        self._poll_scan_progress(progress_queue, progressWin, progressBar)

    def _poll_scan_progress(self, progress_queue, progressWin, progressBar):
        try:
            while True:
                message = progress_queue.get_nowait()
                if message[0] == "progress":
                    _, current, total = message
                    progressBar.configure(maximum=total, value=current)
                elif message[0] == "done":
                    progressWin.destroy()
                    plotFieldAngleScan(message[1])
                    plt.show()
                    return
                elif message[0] == "error":
                    progressWin.destroy()
                    raise message[1]
        except queue.Empty:
            self.root.after(50, self._poll_scan_progress,
                            progress_queue, progressWin, progressBar)


if __name__ == "__main__":

    root = tk.Tk()
    app = RodGUI(root)
    root.mainloop()
