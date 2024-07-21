from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
import tkinter as tk
import matplotlib

matplotlib.use("TkAgg")


class FrameBase(ttk.Frame):
    """
    A base class for displaying numerous labels, entries,
    buttons, or plots.
    """

    def __init__(
        self,
        master: ttk.Frame,
        widget_list: list,
        label_options: dict = None,
        entry_options: dict = None,
        button_options: dict = None,
        plot_options: dict = None,
        combobox_options: dict = None,
        checkbox_options: dict = None,
        radio_options: dict = None,
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
            master (ttk.Frame): Frame in which this frame is embedded.
            widget_list (list): List of widgets to be displayed.
            label_options (dict, optional): Options for labels. Defaults to None.
            entry_options (dict, optional): Options for entries. Defaults to None.
            button_options (dict, optional): Options for buttons. Defaults to None.
            plot_options (dict, optional): Options for plots. Defaults to None.
            combobox_options (dict, optional): Options for comboboxes. Defaults to None.
            checkbox_options (dict, optional): Options for checkboxes. Defaults to None.
            radio_options (dict, optional): Options for radio buttons. Defaults to None.
        """
        super().__init__(master)
        self.widget_list = widget_list
        self.entries = {}
        self.labels = {}
        self.plots = {}
        self.buttons = {}
        self.combobox = {}
        self.checkbox = {}
        self.radios = {}

        self.label_options = label_options or {}
        self.entry_options = entry_options or {}
        self.button_options = button_options or {}
        self.plot_options = plot_options or {}
        self.combobox_options = combobox_options or {}
        self.checkbox_options = checkbox_options or {}
        self.radio_options = radio_options or {}

        self.place_widgets(self.widget_list)
        self.columnconfigure(0, weight=1)

    def delete_all(self):
        """Deletes all widgets from the frame."""
        for widget_dict in [
            self.labels,
            self.entries,
            self.plots,
            self.buttons,
            self.combobox,
            self.checkbox,
            self.radios,
        ]:
            for widget in widget_dict.values():
                widget.grid_forget()
                widget.destroy()
            widget_dict.clear()

    def place_widgets(self, widget_list, row=0, col=0) -> int:
        """Places the widgets in the frame based on the widget_list layout."""
        colspan = self.colspan(widget_list)
        for widget in widget_list:
            row = self.place_widget(widget, row, col, colspan)
        return row

    def place_widget(self, widget, row, col, colspan) -> int:
        """Places a single widget in the frame."""
        if isinstance(widget, list):
            return self.place_sub_widgets(widget, row, col)
        widget_creation_map = {
            "label": self.create_label,
            "entry": self.create_entry,
            "plot": self.create_plot,
            "button": self.create_button,
            "combobox": self.create_combobox,
            "checkbox": self.create_checkbox,
            "radio": self.create_radio,
        }
        for widget_type, creation_func in widget_creation_map.items():
            options_dict = getattr(self, f"{widget_type}_options", {})
            if widget in options_dict:
                creation_func(widget, options_dict[widget], row, col, colspan)
                break
        return row + 1

    def place_sub_widgets(self, sub_widgets, row, col) -> int:
        """Places a list of sub-widgets in the frame."""
        prev_row = row
        for i, sublist in enumerate(sub_widgets):
            row = max(row, self.place_widgets(sublist, prev_row, col + i))
        return row

    def colspan(self, widget_list) -> int:
        """Calculates the column span required for the widget list."""
        return max(
            1,
            max(
                (
                    sum(self.colspan(sublist) if isinstance(sublist, list) else 1 for sublist in widget)
                    for widget in widget_list
                    if isinstance(widget, list)
                ),
                default=0,
            ),
        )

    def create_label(self, key, options, row, col, colspan):
        """Creates and places a label widget."""
        label = tk.Label(self, text=options.get("text", ""))
        label.grid(row=row, column=col, columnspan=colspan, sticky="nsew")
        self.labels[key] = label

    def create_entry(self, key, options, row, col, colspan):
        """Creates and places an entry widget."""
        sv = tk.StringVar(value=options.get("insert", ""))
        sv.trace_add("write", lambda *_: options.get("bindfunc", lambda _: None)(sv))
        entry = tk.Entry(self, textvariable=sv)
        entry.grid(row=row, column=col, columnspan=colspan, sticky="nsew")
        self.entries[key] = entry

    def create_plot(self, key, options, row, col, colspan):
        """Creates and places a plot widget."""
        fig = Figure(figsize=(2, 1.5), dpi=options.get("dpi", 100), tight_layout=True)
        subplot = fig.add_subplot(111)
        subplot.plot(*options.get("xy", ([], [])))
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=row, column=col, columnspan=colspan, sticky="nsew")
        self.plots[key] = canvas.get_tk_widget()

    def create_button(self, key, options, row, col, colspan):
        """Creates and places a button widget."""
        button = ttk.Button(self, text=options.get("text", ""), command=options.get("bindfunc", lambda: None))
        button.grid(row=row, column=col, columnspan=colspan, sticky="nsew")
        self.buttons[key] = button

    def create_combobox(self, key, options, row, col, colspan):
        """Creates and places a combobox widget."""
        combobox = ttk.Combobox(self, values=options.get("values", []), state="readonly")
        combobox.grid(row=row, column=col, columnspan=colspan, sticky="nsew")
        combobox.current(0)
        combobox.bind("<<ComboboxSelected>>", options.get("bindfunc", lambda _: None))
        self.combobox[key] = combobox

    def create_checkbox(self, key, options, row, col, colspan):
        """Creates and places a checkbox widget."""
        var = tk.IntVar(value=options.get("onoff", 0))
        checkbox = ttk.Checkbutton(
            self,
            text=options.get("text", ""),
            variable=var,
            command=lambda: options.get("command", lambda _: None)(var),
        )
        checkbox.grid(row=row, column=col, columnspan=colspan, sticky="nsew")
        self.checkbox[key] = checkbox

    def create_radio(self, key, options, row, col, colspan):
        """Creates and places a radio button widget."""
        radio_frame = ttk.Frame(self)
        var = tk.IntVar(value=options.get("value", 0))
        for text, value in zip(options.get("texts", []), options.get("values", [])):
            radio_button = tk.Radiobutton(
                radio_frame,
                text=text,
                variable=var,
                value=value,
                command=lambda: options.get("command", lambda _: None)(var),
            )
            radio_button.pack(side=tk.LEFT)
        radio_frame.grid(row=row, column=col, columnspan=colspan, sticky="nsew")
        self.radios[key] = radio_frame
