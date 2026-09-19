import tkinter as tk


class ToolTip:

    def __init__(self, widget, text):

        self.widget = widget
        self.text = text
        self.tipwindow = None

        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):

        if self.tipwindow:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20

        self.tipwindow = tw = tk.Toplevel(self.widget)

        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("Arial", 10)
        )

        label.pack()

    def hide_tip(self, event=None):

        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None
