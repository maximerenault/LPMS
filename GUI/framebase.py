from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
import tkinter as tk
import matplotlib

matplotlib.use("TkAgg")


class FrameBase(ttk.Frame):
    """
    A base class for displaying numerous labels, entries,
    buttons or plots.
    """

    def __init__(
        self,
        master: ttk.Frame,
        widget_list: list,
        label_options: dict = {},
        entry_options: dict = {},
        button_options: dict = {},
        plot_options: dict = {},
        cbbox_options: dict = {},
        checkbox_options: dict = {},
        radio_options: dict = {},
    ):
        """From widget_list and the given options, creates all widgets following
        the shape of widget_list as follows :

        widget_list = [widg1, widg2, [[widg3, widg4],[widg5],[widg6]], widg1]
        will give a layout like :
        |      widg1      |
        |      widg2      |
        |widg3|widg5|widg6|
        |widg4|     |     |
        |      widg1      |

        Widgets are generated in the order given in widget list.

        Args:
            master (ttk.Frame): Frame in wich this frame is embedded.
            widget_list (list): List of widgets, see above for more details.
            label_options (dict, optional): See init_widgets for more details. Defaults to {}.
            entry_options (dict, optional): See init_widgets for more details. Defaults to {}.
            button_options (dict, optional): See init_widgets for more details. Defaults to {}.
            plot_options (dict, optional): See init_widgets for more details. Defaults to {}.
            cbbox_options (dict, optional): See init_widgets for more details. Defaults to {}.
        """
        ttk.Frame.__init__(self, master)
        self.widget_list = widget_list
        self.entries = {}
        self.labels = {}
        self.plots = {}
        self.buttons = {}
        self.cbbox = {}
        self.checkbox = {}
        self.radios = {}

        self.label_options = label_options
        self.entry_options = entry_options
        self.button_options = button_options
        self.plot_options = plot_options
        self.cbbox_options = cbbox_options
        self.checkbox_options = checkbox_options
        self.radio_options = radio_options

        self.place_widgets(self.widget_list)
        self.columnconfigure(0, weight=1)

    def delete_all(self):
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
        for bbox in self.cbbox.values():
            bbox.grid_forget()
            bbox.destroy()
        for cbox in self.checkbox.values():
            cbox.grid_forget()
            cbox.destroy()
        for radio in self.radios.values():
            radio.grid_forget()
            radio.destroy()

        # Clear dictionaries
        self.labels.clear()
        self.entries.clear()
        self.plots.clear()
        self.buttons.clear()
        self.cbbox.clear()
        self.checkbox.clear()
        self.radios.clear()

    def place_widgets(self, widget_list, row=0, col=0) -> int:
        colspan = self.colspan(widget_list)
        for widget in widget_list:
            row = self.place_widget(widget, row, col, colspan)
        return row

    def place_widget(self, widget, row, col, colspan) -> int:
        if isinstance(widget, list):
            prevrow = row
            for i, sublist in enumerate(widget):
                row = max(row, self.place_widgets(sublist, prevrow, col + i))
            return row

        elif widget in self.label_options.keys():
            # {"labelkey": {"text": "yourtexthere"}}
            label_dict = self.label_options[widget]
            arg_label = tk.Label(self, text=label_dict["text"])
            arg_label.grid(row=row, column=col, columnspan=colspan, sticky="nsew")

            self.labels[widget] = arg_label

        elif widget in self.entry_options.keys():
            # {"entrykey": {"binfunc": func, "insert": "text"}}
            entry_dict = self.entry_options[widget]
            sv = tk.StringVar(value=entry_dict["insert"])
            sv.trace_add(
                "write", lambda _a, _b, _c, sv=sv: entry_dict["bindfunc"](sv)
            )  # sv=sv prevents garbage collection
            arg_entry = tk.Entry(self, width=10, textvariable=sv)
            arg_entry.grid(row=row, column=col, columnspan=colspan, sticky="nsew")

            self.entries[widget] = arg_entry

        elif widget in self.plot_options.keys():
            # {"plotkey": {"dpi": 100, "xy": (x,y)}}
            plot_dict = self.plot_options[widget]
            font = {"family": "monospace", "size": 7}
            matplotlib.rc("font", **font)
            f = Figure(figsize=(2, 1.5), dpi=plot_dict["dpi"], tight_layout=True)
            subplot = f.add_subplot(111)
            subplot.plot(*plot_dict["xy"])
            arg_canv = FigureCanvasTkAgg(f, self)
            arg_canv.draw()
            arg_canv.get_tk_widget().grid(row=row, column=col, columnspan=colspan, sticky="nsew")

            self.plots[widget] = arg_canv

        elif widget in self.button_options.keys():
            # {"buttonkey": {"bindfunc": func, "text": "title"}}
            button_dict = self.button_options[widget]
            arg_button = ttk.Button(self, command=button_dict["bindfunc"], text=button_dict["text"])
            arg_button.grid(row=row, column=col, columnspan=colspan, sticky="nsew")

            self.buttons[widget] = arg_button

        elif widget in self.cbbox_options.keys():
            # {"cbboxkey": {"values": list(str), "bindfunc": func}}
            cbbox_dict = self.cbbox_options[widget]
            arg_cbbox = ttk.Combobox(self, values=cbbox_dict["values"], state="readonly")
            arg_cbbox.grid(row=row, column=col, columnspan=colspan, sticky="nsew")
            arg_cbbox.current(0)
            arg_cbbox.bind("<<ComboboxSelected>>", cbbox_dict["bindfunc"])

            self.cbbox[widget] = arg_cbbox  # Store combobox in dictionary

        elif widget in self.checkbox_options.keys():
            # {"checkbox": {"text": str, "onoff": 0, "command": func}}
            checkbox_dict = self.checkbox_options[widget]
            var = tk.IntVar()
            var.set(checkbox_dict["onoff"])
            arg_checkbox = ttk.Checkbutton(
                self, text=checkbox_dict["text"], variable=var, command=lambda var=var: checkbox_dict["command"](var)
            )  # var=var prevents garbage collection
            arg_checkbox.grid(row=row, column=col, columnspan=colspan, sticky="nsew")

            self.checkbox[widget] = arg_checkbox  # Store checkbox in dictionary

        elif widget in self.radio_options.keys():
            # {"radio": {"texts": [str], "values": [int], "value": int, "command": func(var)}}
            radio_dict = self.radio_options[widget]
            arg_radio = ttk.Frame(self)
            buttons = zip(radio_dict["texts"], radio_dict["values"])
            var = tk.IntVar()
            var.set(radio_dict["value"])  # Default Select
            for tex, val in buttons:
                radio = tk.Radiobutton(
                    arg_radio, text=tex, variable=var, value=val, command=lambda var=var: radio_dict["command"](var)
                ).pack(side=tk.LEFT)
            arg_radio.grid(row=row, column=col, columnspan=colspan, sticky="nsew")

            self.radios[widget] = arg_radio  # Store checkbox in dictionary

        return row + 1

    def colspan(self, widget_list):
        span = 1
        for widget in widget_list:
            spanwidg = 0
            if isinstance(widget, list):
                for sublist in widget:
                    assert isinstance(sublist, list), "Widget list should contain widgets or lists of lists of widgets"
                    spanwidg += self.colspan(sublist)
            span = max(span, spanwidg)
        return span
