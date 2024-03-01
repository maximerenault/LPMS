from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
import tkinter as tk
import networkx as nx
import matplotlib

matplotlib.use("TkAgg")


class FrameSolve(ttk.Frame):
    """
    A class for choosing simulation parameters
    """

    def __init__(self, master, drbd):
        ttk.Frame.__init__(self, master)
        self.entries = {}
        self.comboboxes = {}
        self.labels = {}
        self.plots = {}
        self.buttons = {}

        self.associated_widgets = {
            "solver": [
                "timestep",
                "time integration",
                #   "conn_mat",
                "Solve",
                "Export matrices",
            ]
        }

        self.entry_options = {
            "timestep": {"bg": "light yellow", "bindfunc": self.update_timestep},
        }

        self.cbbox_options = {
            "time integration": {"values": drbd.csolver.time_integrations, "bindfunc": self.update_time_integration},
        }

        self.plot_options = {
            "conn_mat": {"dpi": 100},
        }

        self.button_options = {
            "Solve": {"text": "Solve", "bindfunc": self.solve},
            "Export matrices": {"text": "Delete", "bindfunc": self.export_matrices},
        }

        self.status = tk.StringVar()
        self.status.set("Simulation parameters panel\nPress Enter to validate")
        self.instructions = tk.Label(self, textvariable=self.status)
        self.instructions.grid(row=0, column=1, sticky="we")

        self.drbd = drbd

    def update_timestep(self, event):
        """
        Update timestep of simulation
        """
        dt = float(self.entries["timestep"].get())
        self.drbd.csolver.set_dt(dt)

    def update_time_integration(self, event):
        """
        Update time integration scheme
        """
        self.drbd.csolver.set_time_integration(self.comboboxes["time integration"].get())

    def solve(self):
        return

    def export_matrices(self):
        return

    def update_framesolve(self):
        # Destroy existing labels and entries
        for label in self.labels.values():
            label.grid_forget()
            label.destroy()
        for entry in self.entries.values():
            entry.grid_forget()
            entry.destroy()
        for cbbox in self.comboboxes.values():
            cbbox.grid_forget()
            cbbox.destroy()
        for plot in self.plots.values():
            plot.get_tk_widget().grid_forget()
            plot.get_tk_widget().destroy()
        for button in self.buttons.values():
            button.grid_forget()
            button.destroy()

        # Clear dictionaries
        self.labels.clear()
        self.entries.clear()
        self.comboboxes.clear()
        self.plots.clear()
        self.buttons.clear()

        csolver = self.drbd.csolver

        row = 1
        # Create new labels and entries based on associated widgets
        for widget in self.associated_widgets["solver"]:
            if widget in self.entry_options.keys():
                arg_label = tk.Label(self, text=widget + ":")
                arg_label.grid(row=row, column=0)

                arg_entry = tk.Entry(self, width=10, bg=self.entry_options[widget]["bg"])
                arg_entry.grid(row=row, column=1, sticky="we")
                arg_entry.bind("<Return>", self.entry_options[widget]["bindfunc"])

                # Fill the widget with element attributes
                if widget == "timestep":
                    arg_entry.insert(tk.END, csolver.get_dt())

                self.labels[widget] = arg_label  # Store label in dictionary
                self.entries[widget] = arg_entry  # Store entry in dictionary

            if widget in self.cbbox_options.keys():
                arg_label = tk.Label(self, text=widget + ":")
                arg_label.grid(row=row, column=0)

                arg_cbbox = ttk.Combobox(self, values=self.cbbox_options[widget]["values"], state="readonly")
                arg_cbbox.grid(row=row, column=1)
                arg_cbbox.current(0)
                csolver.set_time_integration(self.cbbox_options[widget]["values"][0])
                arg_cbbox.bind("<<ComboboxSelected>>", self.cbbox_options[widget]["bindfunc"])

                self.labels[widget] = arg_label  # Store label in dictionary
                self.comboboxes[widget] = arg_cbbox  # Store combobox in dictionary

            if widget in self.plot_options.keys():
                font = {"family": "monospace", "size": 7}
                matplotlib.rc("font", **font)
                f = Figure(figsize=(2, 1.5), dpi=self.plot_options[widget]["dpi"], tight_layout=True)
                subplot = f.add_subplot(111)
                Graph = nx.from_numpy_array(self.drbd.cgraph.conn_mat)
                nx.draw_networkx(
                    Graph,
                    edge_color=tuple(
                        (
                            "silver"
                            if Graph[u][v]["weight"] == 1
                            else (
                                "red"
                                if Graph[u][v]["weight"] == 2
                                else (
                                    "indigo"
                                    if Graph[u][v]["weight"] == 3
                                    else (
                                        "coral"
                                        if Graph[u][v]["weight"] == 4
                                        else "goldenrod" if Graph[u][v]["weight"] == 6 else "pink"
                                    )
                                )
                            )
                        )
                        for u, v in Graph.edges()
                    ),
                    width=3,
                    ax=subplot,
                )
                arg_canv = FigureCanvasTkAgg(f, self)
                arg_canv.draw()
                arg_canv.get_tk_widget().grid(row=row, column=1, sticky="we")

                self.plots[widget] = arg_canv

            if widget in self.button_options.keys():
                arg_button = ttk.Button(
                    self, command=self.button_options[widget]["bindfunc"], text=self.button_options[widget]["text"]
                )
                arg_button.grid(row=row, column=1, sticky="we")

                self.buttons[widget] = arg_button  # Store button in dictionary

            row += 1
        return
