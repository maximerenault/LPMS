from matplotlib import tight_layout
from utils.io import readvalues
import numpy as np
import scipy as sp
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
import tkinter as tk
from elements.wire import Wire
from elements.resistor import Resistor
from elements.capacitor import Capacitor
from elements.inductor import Inductor
from elements.ground import Ground
from elements.psource import PSource
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("TkAgg")


class Attributes(ttk.Frame):
    """
    A class for displaying info about an element
    and editing it
    """

    def __init__(self, master, drbd):
        ttk.Frame.__init__(self, master)
        self.entries = {}
        self.labels = {}
        self.plots = {}
        self.buttons = {}

        self.associated_widgets = {
            "Wire": ["name", "start", "end", "delete"],
            "Dipole": ["name", "start", "end", "value", "delete"],
            "Ground": ["name", "start", "end", "delete"],
            "Source": ["name", "start", "end", "period", "source", "read", "delete"],
        }

        self.entry_options = {
            "name": {"bg": "light yellow", "bindfunc": self.update_name},
            "value": {"bg": "light yellow", "bindfunc": self.update_value},
            "start": {"bg": "light blue", "bindfunc": lambda event: self.update_coords(event, "start")},
            "end": {"bg": "light blue", "bindfunc": lambda event: self.update_coords(event, "end")},
            "period": {"bg": "light yellow", "bindfunc": self.update_period},
        }

        self.plot_options = {"source": {"dpi": 100}}

        self.button_options = {
            "read": {"text": "Read file", "bindfunc": self.read_values},
            "delete": {"text": "Delete", "bindfunc": self.delete_elem},
        }

        self.status = tk.StringVar()
        self.status.set("Attributes edition panel")
        self.instructions = tk.Label(self, textvariable=self.status)
        self.instructions.grid(row=0, column=1, sticky="we")

        self.drbd = drbd
        self.elem = -1

    def update_name(self, event):
        if self.elem == -1:
            self.update_attributes()
            return
        el = self.drbd.cgraph.elems[self.elem]
        el.name = self.entries["name"].get()
        el.redrawname(self.drbd)

    def update_coords(self, event, widget):
        if self.elem == -1:
            self.update_attributes()
            return
        el = self.drbd.cgraph.elems[self.elem]
        xy = self.entries[widget].get()
        try:
            xy = xy.split(",")
            x = int(xy[0])
            y = int(xy[1])
            if widget == "start":
                el.nodes[0].setcoords(x, y)
            elif widget == "end":
                el.setend(x, y)
            else:
                raise "Error: incorrect widget"
            el.redraw(self.drbd)
            self.update_attributes()
        except:
            print("Error with " + widget + " coords")

    def update_value(self, event):
        if self.elem == -1:
            self.update_attributes()
            return
        el = self.drbd.cgraph.elems[self.elem]
        try:
            val = float(self.entries["value"].get())
            el.set_value(val)
            self.update_attributes()
        except:
            print("Error with value input")

    def update_period(self, event):
        if self.elem == -1:
            self.update_attributes()
            return
        el = self.drbd.cgraph.elems[self.elem]
        try:
            period = float(self.entries["period"].get())
            el.set_period(period)
            self.update_attributes()
        except:
            print("Error with period input")

    def read_values(self):
        file_io = tk.filedialog.askopenfilename()
        if file_io:
            x, y = readvalues(file_io)
            el = self.drbd.cgraph.elems[self.elem]
            source = sp.interpolate.CubicSpline(x, y, extrapolate="periodic")
            el.set_source(source)
            self.update_attributes()

    def delete_elem(self):
        if self.elem == -1:
            self.update_attributes()
            return
        self.drbd.deleteElement(self.elem)
        self.elem = -1
        self.update_attributes()

    def change_elem(self, id):
        """
        Interface function for other modules
        to change the element selected

        id : int, unique id number of the element
        """
        self.elem = id
        self.update_attributes()

    def update_attributes(self):
        # Destroy existing labels and entries
        for label in self.labels.values():
            label.grid_forget()
            label.destroy()
        for entry in self.entries.values():
            entry.grid_forget()
            entry.destroy()
        for plot in self.plots.values():
            plot.get_tk_widget().grid_forget()
            plot.get_tk_widget().destroy()
        for button in self.buttons.values():
            button.grid_forget()
            button.destroy()

        # Clear dictionaries
        self.labels.clear()
        self.entries.clear()
        self.plots.clear()
        self.buttons.clear()

        self.status.set("Attributes edition panel")

        if self.elem == -1:
            return

        self.status.set("Press Enter to validate")

        el = self.drbd.cgraph.elems[self.elem]
        coords = el.getcoords()

        if isinstance(el, Resistor) or isinstance(el, Inductor) or isinstance(el, Capacitor):
            elemtype = "Dipole"
        elif type(el) == Wire:
            elemtype = "Wire"  # Careful with inheritance and isinstance
        elif isinstance(el, PSource):
            elemtype = "Source"
        elif isinstance(el, Ground):
            elemtype = "Ground"
        else:
            raise "No idea what this object is"

        row = 1
        # Create new labels and entries based on associated widgets
        for widget in self.associated_widgets[elemtype]:
            if widget in self.entry_options.keys():
                arg_label = tk.Label(self, text=widget + ":")
                arg_label.grid(row=row, column=0)

                arg_entry = tk.Entry(self, width=10, bg=self.entry_options[widget]["bg"])
                arg_entry.grid(row=row, column=1, sticky="we")
                arg_entry.bind("<Return>", self.entry_options[widget]["bindfunc"])

                # Fill the widget with element attributes
                if widget == "name":
                    arg_entry.insert(tk.END, el.name)
                elif widget == "start":
                    arg_entry.insert(tk.END, str(coords[0]) + "," + str(coords[1]))
                elif widget == "end":
                    arg_entry.insert(tk.END, str(coords[2]) + "," + str(coords[3]))
                elif widget == "value":
                    arg_entry.insert(tk.END, el.get_value())
                elif widget == "period":
                    arg_entry.insert(tk.END, el.get_period())

                self.labels[widget] = arg_label  # Store label in dictionary
                self.entries[widget] = arg_entry  # Store entry in dictionary

            if widget in self.plot_options.keys():
                font = {"family": "monospace", "size": 7}
                matplotlib.rc("font", **font)
                f = Figure(figsize=(2, 1.5), dpi=self.plot_options[widget]["dpi"], tight_layout=True)
                subplot = f.add_subplot(111)
                xs = np.linspace(0, el.get_period(), 50)
                subplot.plot(xs, el.get_source()(xs))
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
