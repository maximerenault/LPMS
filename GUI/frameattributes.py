from GUI.framebase import FrameBase
from utils.io import readvalues
import numpy as np
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
from exceptions.attibutesexceptions import *
from utils.strings import *
import matplotlib
import utils.calculator as calc

matplotlib.use("TkAgg")


class FrameAttributes(ttk.Frame):
    """
    A class for displaying info about an element
    and editing it
    """

    def __init__(self, master, drbd):
        ttk.Frame.__init__(self, master)
        self.rowconfigure((0, 2), weight=1)
        self.columnconfigure(0, weight=1)

        self.widget_lists = {
            "Clear": ["clear"],
            "Wire": [
                [
                    ["labnam", "labsta", "lablisten", "labend", "lablisten", "lablistenQ"],
                    ["name", [["startx"], ["starty"]], "listenPstart", [["endx"], ["endy"]], "listenPend", "listenQ"],
                ],
                "delete",
            ],
            "Dipole": [
                [
                    ["labnam", "labsta", "lablisten", "labend", "lablisten", "labval", "lablistenQ"],
                    ["name", [["startx"], ["starty"]], "listenPstart", [["endx"], ["endy"]], "listenPend", "value", "listenQ"]
                ],
                "delete",
            ],
            "Ground": [[["labnam", "labsta", "labdir"], ["name", [["startx"], ["starty"]], "direction"]], "delete"],
            "Source": [
                [["labnam", "labsta", "labdir"], ["name", [["startx"], ["starty"]], "direction"]],
                "source",
                "read",
                "delete",
            ],
        }

        self.rowcol_weigths = {
            "Clear": {"rows": [0], "rowweights": [1], "cols": [0], "colweights": [1]},
            "Wire": {"rows": [], "rowweights": [], "cols": [1, 2], "colweights": [1, 1]},
            "Dipole": {"rows": [], "rowweights": [], "cols": [1, 2], "colweights": [1, 1]},
            "Ground": {"rows": [], "rowweights": [], "cols": [1, 2], "colweights": [1, 1]},
            "Source": {"rows": [], "rowweights": [], "cols": [1, 2], "colweights": [1, 1]},
        }

        self.label_options = {
            "labnam": {"text": "Name"},
            "labval": {"text": "Value"},
            "labsta": {"text": "Start"},
            "lablisten": {"text": "Listen"},
            "lablistenQ": {"text": "Listen Q"},
            "labend": {"text": "End"},
            "labdir": {"text": "Direction"},
            "clear": {"text": "Attributes edition panel"},
        }

        self.entry_options = {
            "name": {"bindfunc": self.update_name, "insert": ""},
            "value": {"bindfunc": self.update_value, "insert": ""},
            "startx": {"bindfunc": lambda stringvar: self.update_coords(stringvar, "start", "x"), "insert": ""},
            "starty": {"bindfunc": lambda stringvar: self.update_coords(stringvar, "start", "y"), "insert": ""},
            "endx": {"bindfunc": lambda stringvar: self.update_coords(stringvar, "end", "x"), "insert": ""},
            "endy": {"bindfunc": lambda stringvar: self.update_coords(stringvar, "end", "y"), "insert": ""},
        }

        self.cbbox_options = {
            "direction": {"values": ["S", "E", "N", "W"], "bindfunc": self.update_direction},
        }

        self.plot_options = {"source": {"dpi": 100, "xy": ([0, 1], [0, 1])}}

        self.button_options = {
            "read": {"text": "Read file", "bindfunc": self.read_values},
            "delete": {"text": "Delete", "bindfunc": self.delete_elem},
        }

        self.checkbox_options = {
            "listenPstart": {"text": "on/off", "onoff": 0, "command": lambda: self.change_listenP(0)},
            "listenPend": {"text": "on/off", "onoff": 0, "command": lambda: self.change_listenP(1)},
        }

        self.radio_options = {
            "listenQ": {"texts": ["off", "Q", "-Q"], "values": [0, 1, -1], "command": self.set_listenQ},
        }

        self.widget_frame = FrameBase(self, [])
        self.update_widget_list()

        self.drbd = drbd
        self.elem = -1

    def update_name(self, stringvar):
        """
        Update name of the object and
        display it
        """
        if self.elem == -1:
            self.update_attributes()
            return
        el = self.drbd.cgeom.elems[self.elem]
        el.name = stringvar.get()
        el.redrawname(self.drbd)

    def update_coords(self, stringvar, pos, comp):
        """
        Updates start or end coords of the object
        with id self.elem
        """
        if self.elem == -1:
            self.update_attributes()
            return
        el = self.drbd.cgeom.elems[self.elem]
        coords = el.getcoords()
        newcoord = check_strint(stringvar.get())
        stringvar.set(newcoord)
        if newcoord == "" or newcoord == "-":
            return
        try:
            newcoordint = int(newcoord)
        except:
            raise BadNumberError(newcoord)
        if pos == "start":
            if comp == "x":
                el.setstart(newcoordint, coords[1])
            elif comp == "y":
                el.setstart(coords[0], newcoordint)
        elif pos == "end":
            if comp == "x":
                el.setend(newcoordint, coords[3])
            elif comp == "y":
                el.setend(coords[2], newcoordint)
        else:
            raise BadCoordError
        newcoords = el.getcoords()
        if (newcoords[:2] == newcoords[2:]).all():
            el.setstart(coords[0], coords[1])
            el.setend(coords[2], coords[3])
            return
        el.redraw(self.drbd)

    def update_value(self, stringvar):
        """
        Updates value for dipole elements
        """
        if self.elem == -1:
            self.update_attributes()
            return
        el = self.drbd.cgeom.elems[self.elem]
        valstr = check_strfloat(stringvar.get())
        stringvar.set(valstr)
        if valstr == "" or valstr == "-":
            return
        try:
            val = float(valstr)
            el.set_value(val)
        except:
            raise BadNumberError(valstr)

    def read_values(self):
        """
        Allows for opening a csv file
        with columns time and value,
        with sep='\t'
        """
        file_name = tk.filedialog.askopenfilename()
        if file_name:
            x, y = readvalues(file_name)
            el = self.drbd.cgeom.elems[self.elem]
            el.set_source(x, y)
            self.update_attributes()

    def update_direction(self, event: tk.Event):
        """
        Update source-type element direction
        """
        el = self.drbd.cgeom.elems[self.elem]
        coords = el.getcoords()
        dirx = event.widget.get()
        if dirx == "S":
            el.setend(coords[0], coords[1] - 1)
        elif dirx == "E":
            el.setend(coords[0] + 1, coords[1])
        elif dirx == "N":
            el.setend(coords[0], coords[1] + 1)
        elif dirx == "W":
            el.setend(coords[0] - 1, coords[1])
        el.redraw(self.drbd)

    def change_listenP(self, pos):
        """
        Change pressure listening from True to False
        and the other way around.
        """
        el = self.drbd.cgeom.elems[self.elem]
        el.toggle_listenP(pos)
        el.redraw(self.drbd)

    def set_listenQ(self, var):
        """
        Set Q listening flag to 0 if off, 1 if same direction
        as elem, -1 otherwise.
        """
        el = self.drbd.cgeom.elems[self.elem]
        val = var.get()
        el.set_listenQ(val)
        el.redraw(self.drbd)

    def delete_elem(self):
        """
        Calls deleteElement from the
        drawing board and resets attributes.
        """
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

    def update_widget_list(self, key: str = "Clear"):
        self.widget_frame.delete_all()
        del self.widget_frame
        self.widget_frame = FrameBase(
            self,
            self.widget_lists[key],
            self.label_options,
            self.entry_options,
            self.button_options,
            self.plot_options,
            self.cbbox_options,
            self.checkbox_options,
            self.radio_options,
        )
        self.widget_frame.grid(row=1, column=0, sticky="nsew")
        for i, row in enumerate(self.rowcol_weigths[key]["rows"]):
            w = self.rowcol_weigths[key]["rowweights"][i]
            self.widget_frame.rowconfigure(row, weight=w)
        for i, col in enumerate(self.rowcol_weigths[key]["cols"]):
            w = self.rowcol_weigths[key]["colweights"][i]
            self.widget_frame.columnconfigure(col, weight=w)

    def update_attributes(self):
        if self.elem == -1:
            self.update_widget_list()
            return

        el = self.drbd.cgeom.elems[self.elem]

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

        coords = el.getcoords()
        self.entry_options["name"]["insert"] = el.name
        self.entry_options["value"]["insert"] = el.value
        self.entry_options["startx"]["insert"] = coords[0]
        self.entry_options["starty"]["insert"] = coords[1]
        self.entry_options["endx"]["insert"] = coords[2]
        self.entry_options["endy"]["insert"] = coords[3]

        self.checkbox_options["listenPstart"]["onoff"] = int(el.get_listenP(0))
        self.checkbox_options["listenPend"]["onoff"] = int(el.get_listenP(1))

        if el.active == True:
            x = np.linspace(0, 10, 100)
            y = calc.calculate(el.get_value())[0](x)
            self.plot_options["source"]["xy"] = (x, y)

        self.update_widget_list(elemtype)
