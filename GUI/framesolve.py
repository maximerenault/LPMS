from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from GUI.framebase import FrameBase
from tkinter import ttk
import tkinter as tk
import networkx as nx
import matplotlib
from exceptions.solveframeexceptions import *
from solvers.circuitgraph import CircuitGraph
from solvers.circuitsolver import CircuitSolver
from utils.strings import *

matplotlib.use("TkAgg")


class FrameSolve(ttk.Frame):
    """
    A class for choosing simulation parameters
    """

    def __init__(self, master, drbd):
        ttk.Frame.__init__(self, master)
        self.rowconfigure((0, 2), weight=1)
        self.columnconfigure(0, weight=1)

        self.widget_lists = {
            "Clear": ["labpanel"],
            "Solver": [
                "labpanel",
                [["labdt", "labmaxtime", "labtimeint"], ["timestep", "maxtime", "time integration"]],
                # "conn_mat",
                "Solve",
                "Export matrices",
            ],
        }

        self.rowcol_weigths = {
            "Clear": {"rows": [0], "rowweights": [1], "cols": [0], "colweights": [1]},
            "Solver": {"rows": [], "rowweights": [], "cols": [1], "colweights": [1]},
        }

        self.label_options = {
            "labpanel": {"text": "Simulation parameters panel"},
            "labdt": {"text": "Timestep"},
            "labmaxtime": {"text": "Max time"},
            "labtimeint": {"text": "Integration scheme"},
        }

        self.csolver = CircuitSolver()

        self.entry_options = {
            "timestep": {"bindfunc": self.update_timestep, "insert": self.csolver.get_dt()},
            "maxtime": {"bindfunc": self.update_maxtime, "insert": self.csolver.get_maxtime()},
        }

        self.cbbox_options = {
            "time integration": {"values": self.csolver.time_integrations, "bindfunc": self.update_time_integration},
        }

        self.plot_options = {
            "conn_mat": {"dpi": 100},
        }

        self.button_options = {
            "Solve": {"text": "Solve", "bindfunc": self.solve},
            "Export matrices": {"text": "Export matrices", "bindfunc": self.export_matrices},
        }

        self.widget_frame = FrameBase(self, [])
        self.update_widget_list("Solver")

        self.drbd = drbd

    def update_timestep(self, stringvar):
        """
        Update timestep of simulation
        """
        dtstr = check_strfloat_pos(stringvar.get())
        stringvar.set(dtstr)
        if dtstr == "" or dtstr == ".":
            return
        try:
            dt = float(dtstr)
            self.csolver.set_dt(dt)
        except:
            raise BadNumberError(dtstr)

    def update_maxtime(self, stringvar):
        """
        Update max time of simulation
        """
        mtstr = check_strfloat_pos(stringvar.get())
        stringvar.set(mtstr)
        if mtstr == "" or mtstr == ".":
            return
        try:
            mt = float(mtstr)
            self.csolver.set_maxtime(mt)
        except:
            raise BadNumberError(mtstr)

    def update_time_integration(self, event: tk.Event):
        """
        Update time integration scheme
        """
        self.csolver.set_time_integration(event.widget.get())

    def solve(self):
        # Pre-solving operations : removing wires, creating readable graph
        if len(self.drbd.cgeom.nodes) == 0:
            tk.messagebox.showerror("Error", "No system to solve")
            return
        cgraph = CircuitGraph(self.drbd.cgeom.nodes, self.drbd.cgeom.elems)
        # conn_comp = self.drbd.cgraph.pre_solve()
        # if conn_comp != 1:
        #     tk.messagebox.showerror("Error", "Too many connected components in graph")
        #     return
        # if len(self.drbd.cgraph.graph_conn_mat) == 1:
        #     tk.messagebox.showerror("Error", "Isolated node in the graph (short-circuit)")
        #     return
        
        # Solving operations
        Paths, StartEnds = cgraph.graph_max_len_non_branching_paths()
        nbQ = len(Paths)
        nbP = len([n for n in cgraph.nodes if n.type != "Source"])
        cns = self.csolver.solve(nbP, nbQ, cgraph.nodes, Paths, StartEnds)
        if cns == 1:
            tk.messagebox.showerror("Error", "The problem is under constrained, add a source")
            return
        if cns == 2:
            tk.messagebox.showerror("Error", "The problem is over constrained, remove a source")
            return
        return

    def export_matrices(self):
        return

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
        )
        self.widget_frame.grid(row=1, column=0, sticky="nsew")
        for i, row in enumerate(self.rowcol_weigths[key]["rows"]):
            w = self.rowcol_weigths[key]["rowweights"][i]
            self.widget_frame.rowconfigure(row, weight=w)
        for i, col in enumerate(self.rowcol_weigths[key]["cols"]):
            w = self.rowcol_weigths[key]["colweights"][i]
            self.widget_frame.columnconfigure(col, weight=w)

    # def update_framesolve(self):
    #     # Destroy existing labels and entries
    #     for label in self.labels.values():
    #         label.grid_forget()
    #         label.destroy()
    #     for entry in self.entries.values():
    #         entry.grid_forget()
    #         entry.destroy()
    #     for cbbox in self.comboboxes.values():
    #         cbbox.grid_forget()
    #         cbbox.destroy()
    #     for plot in self.plots.values():
    #         plot.get_tk_widget().grid_forget()
    #         plot.get_tk_widget().destroy()
    #     for button in self.buttons.values():
    #         button.grid_forget()
    #         button.destroy()

    #     # Clear dictionaries
    #     self.labels.clear()
    #     self.entries.clear()
    #     self.comboboxes.clear()
    #     self.plots.clear()
    #     self.buttons.clear()

    #     csolver = self.drbd.csolver

    #     row = 1
    #     # Create new labels and entries based on associated widgets
    #     for widget in self.associated_widgets["solver"]:
    #         if widget in self.entry_options.keys():
    #             arg_label = tk.Label(self, text=widget + ":")
    #             arg_label.grid(row=row, column=0)

    #             arg_entry = tk.Entry(self, width=10, bg=self.entry_options[widget]["bg"])
    #             arg_entry.grid(row=row, column=1, sticky="we")
    #             arg_entry.bind("<Return>", self.entry_options[widget]["bindfunc"])

    #             # Fill the widget with element attributes
    #             if widget == "timestep":
    #                 arg_entry.insert(tk.END, csolver.get_dt())
    #             elif widget == "max time":
    #                 arg_entry.insert(tk.END, csolver.get_maxtime())

    #             self.labels[widget] = arg_label  # Store label in dictionary
    #             self.entries[widget] = arg_entry  # Store entry in dictionary

    #         if widget in self.cbbox_options.keys():
    #             arg_label = tk.Label(self, text=widget + ":")
    #             arg_label.grid(row=row, column=0)

    #             arg_cbbox = ttk.Combobox(self, values=self.cbbox_options[widget]["values"], state="readonly")
    #             arg_cbbox.grid(row=row, column=1)
    #             arg_cbbox.current(0)
    #             csolver.set_time_integration(self.cbbox_options[widget]["values"][0])
    #             arg_cbbox.bind("<<ComboboxSelected>>", self.cbbox_options[widget]["bindfunc"])

    #             self.labels[widget] = arg_label  # Store label in dictionary
    #             self.comboboxes[widget] = arg_cbbox  # Store combobox in dictionary

    #         if widget in self.plot_options.keys():
    #             font = {"family": "monospace", "size": 7}
    #             matplotlib.rc("font", **font)
    #             f = Figure(figsize=(2, 1.5), dpi=self.plot_options[widget]["dpi"], tight_layout=True)
    #             subplot = f.add_subplot(111)
    #             subplot.matshow(self.drbd.cgraph.conn_mat)
    #             # Graph = nx.from_numpy_array(self.drbd.cgraph.conn_mat)
    #             # nx.draw_networkx(
    #             #     Graph,
    #             #     edge_color=tuple(
    #             #         (
    #             #             "silver"
    #             #             if Graph[u][v]["weight"] == 1
    #             #             else (
    #             #                 "red"
    #             #                 if Graph[u][v]["weight"] == 2
    #             #                 else (
    #             #                     "indigo"
    #             #                     if Graph[u][v]["weight"] == 3
    #             #                     else (
    #             #                         "coral"
    #             #                         if Graph[u][v]["weight"] == 4
    #             #                         else "goldenrod" if Graph[u][v]["weight"] == 6 else "pink"
    #             #                     )
    #             #                 )
    #             #             )
    #             #         )
    #             #         for u, v in Graph.edges()
    #             #     ),
    #             #     width=3,
    #             #     ax=subplot,
    #             # )
    #             arg_canv = FigureCanvasTkAgg(f, self)
    #             arg_canv.draw()
    #             arg_canv.get_tk_widget().grid(row=row, column=1, sticky="we")

    #             self.plots[widget] = arg_canv

    #         if widget in self.button_options.keys():
    #             arg_button = ttk.Button(
    #                 self, command=self.button_options[widget]["bindfunc"], text=self.button_options[widget]["text"]
    #             )
    #             arg_button.grid(row=row, column=1, sticky="we")

    #             self.buttons[widget] = arg_button  # Store button in dictionary

    #         row += 1
    #     return
