import numpy as np
from control import TransferFunction, forced_response
from tkinter import Tk, Label, Entry, StringVar, DoubleVar, ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class RealTimeSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerçek Zamanlı Sistem Simülatörü")

        # Define all instance attributes
        self.numerator_entry = None
        self.denominator_entry = None
        self.gain_entry = None
        self.input_menu = None
        self.fig = None
        self.ax = None
        self.line = None
        self.canvas = None

        # Default system (transfer function)
        self.numerator = [1.0]
        self.denominator = [1.0, 2.0, 1.0]
        self.system = TransferFunction(self.numerator, self.denominator)

        # Gain and input type
        self.gain = DoubleVar(value=1.0)
        self.input_type = StringVar(value="step")

        # Time vector and signals
        self.t = np.linspace(0, 10, 1000)
        self.u = np.ones_like(self.t)  # Default step input
        self.y = np.zeros_like(self.t)

        # GUI setup
        self.create_widgets()
        self.create_plot()

        # Update plot in real time
        self.update_plot()

    def create_widgets(self):
        # Numerator input
        Label(self.root, text="Pay Katsayıları:").grid(row=0, column=0, sticky="w")
        self.numerator_entry = Entry(self.root)
        self.numerator_entry.insert(0, "1")
        self.numerator_entry.grid(row=0, column=1)
        self.numerator_entry.bind("<KeyRelease>", self.update_system)

        # Denominator input
        Label(self.root, text="Payda Katsayıları:").grid(row=1, column=0, sticky="w")
        self.denominator_entry = Entry(self.root)
        self.denominator_entry.insert(0, "1 2 1")
        self.denominator_entry.grid(row=1, column=1)
        self.denominator_entry.bind("<KeyRelease>", self.update_system)

        # Gain input
        Label(self.root, text="Kazanç:").grid(row=2, column=0, sticky="w")
        self.gain_entry = Entry(self.root, textvariable=self.gain)
        self.gain_entry.grid(row=2, column=1)
        self.gain_entry.bind("<KeyRelease>", self.update_system)

        # Input type dropdown
        Label(self.root, text="Giriş Tipi:").grid(row=3, column=0, sticky="w")
        self.input_menu = ttk.Combobox(self.root, textvariable=self.input_type, state="readonly")
        self.input_menu["values"] = ["step", "ramp", "sinusoidal"]
        self.input_menu.grid(row=3, column=1)
        self.input_menu.bind("<<ComboboxSelected>>", self.update_system)

    def create_plot(self):
        # Create Matplotlib figure and axes
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Sistem Cevabı")
        self.ax.set_xlabel("Zaman")
        self.ax.set_ylabel("Çıkış")
        self.ax.grid(True)

        # Initial plot
        self.line, = self.ax.plot(self.t, self.y)

        # Embed Matplotlib plot in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.grid(row=5, column=0, columnspan=2)

    def update_system(self, _=None):
        # Update the transfer function
        try:
            numerator = list(map(float, self.numerator_entry.get().split()))
            denominator = list(map(float, self.denominator_entry.get().split()))
            gain = self.gain.get()

            # Check for proper transfer function
            if len(numerator) >= len(denominator):
                raise ValueError("The numerator degree must be less than the denominator degree.")

            # Create the transfer function
            self.system = TransferFunction([gain * n for n in numerator], denominator)

            # Update input signal
            if self.input_type.get() == "step":
                self.u = np.ones_like(self.t)
            elif self.input_type.get() == "ramp":
                self.u = self.t
            elif self.input_type.get() == "sinusoidal":
                self.u = np.sin(2 * np.pi * 0.5 * self.t)
            else:
                self.u = np.zeros_like(self.t)

        except ValueError as e:
            # Show an error message and reset to the default system
            messagebox.showerror("Geçersiz Giriş", f"Hata: {e}")
            self.system = TransferFunction([1.0], [1.0, 2.0, 1.0])

    def simulate(self):
        # Calculate the system response
        t_out, y_out = forced_response(self.system, T=self.t, U=self.u)
        return y_out

    def update_plot(self):
        # Update plot with the latest simulation data
        self.y = self.simulate()
        self.line.set_ydata(self.y)
        self.ax.relim()
        self.ax.autoscale_view()

        # Redraw the canvas
        self.canvas.draw()

        # Schedule the next update
        self.root.after(100, self.update_plot)


if __name__ == "__main__":
    main_window = Tk()
    app = RealTimeSimulator(main_window)
    main_window.mainloop()
