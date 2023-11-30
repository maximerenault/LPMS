from GUI.gridzoom import GridZoom
from elements.wire import Wire
from elements.resistor import Resistor
from elements.capacitor import Capacitor
from elements.inductor import Inductor
import tkinter as tk
from tkinter import ttk

class DrawingBoard(GridZoom):
    def __init__(self, mainframe):
        ''' Initialize the main Frame '''
        GridZoom.__init__(self, mainframe)
        # Bind events to the Canvas
        self.canvas.bind('<Configure>', self.dr_resize)  # canvas is resized
        self.canvas.bind('<ButtonPress-1>',     self.dr_move_from)
        self.canvas.bind('<B1-Motion>',         self.dr_move_to)
        self.canvas.bind('<MouseWheel>', self.dr_wheel)  # with Windows and MacOS, but not Linux
        self.canvas.bind('<Button-5>',   self.dr_wheel)  # only with Linux, wheel scroll down
        self.canvas.bind('<Button-4>',   self.dr_wheel)  # only with Linux, wheel scroll up
        self.frameChoices = ttk.Frame(self.master)
        self.frameChoices.grid(row=2, column=0, pady=1)
        self.radiovalue = tk.StringVar()
        self.radiovalue.set("Move") #Default Select
        self.drag_functions = ["Move", "Wire", "R", "C", "L"]
        for fc in self.drag_functions:
            radio = tk.Radiobutton(self.frameChoices, text=fc, variable=self.radiovalue, font="comicsans     12 bold", value=fc, command=self.dragchanger).pack(side=tk.LEFT, padx=6,pady=3)
        self.drag_function = "Move"
        self.board_elems = []
    
    def dr_resize(self, event):
        dx, dy = self.resize()
        self.canvas.move("circuit", dx, dy)

    def dr_move_from(self, event):
        self.move_from(event)
        x0, y0 = self.pix2coord(self.prevx, self.prevy)
        x0 = round(x0)
        y0 = round(y0)
        if self.drag_function == "Wire" :
            wire = Wire(self, x0, y0, x0, y0)
            wire.draw()
            self.board_elems.append(wire)
        if self.drag_function == "R" :
            resistor = Resistor(self, x0, y0, x0, y0, 10)
            resistor.draw()
            self.board_elems.append(resistor)
        if self.drag_function == "C" :
            capacitor = Capacitor(self, x0, y0, x0, y0, 10)
            capacitor.draw()
            self.board_elems.append(capacitor)
        if self.drag_function == "L" :
            inductor = Inductor(self, x0, y0, x0, y0, 10)
            inductor.draw()
            self.board_elems.append(inductor)

    def dr_move_to(self, event):
        if self.drag_function == "Move" :
            self.canvas.move("circuit", event.x - self.prevx, event.y - self.prevy)
            self.move_to(event)
        elif self.drag_function == "Wire" \
            or self.drag_function == "R" \
            or self.drag_function == "C" \
            or self.drag_function == "L" :
            x1, y1 = self.pix2coord(event.x, event.y)
            x1 = round(x1)
            y1 = round(y1)
            elem = self.board_elems[-1]
            elem.coords[2] = x1
            elem.coords[3] = y1
            elem.redraw()
            self.show_frontground(event)

    def dr_wheel(self, event):
        self.gridwheel(event)
        for el in self.board_elems :
            el.redraw()

    def dragchanger(self, event=None):
        self.drag_function = self.radiovalue.get() #selected radio value
    
    def deleteElement(self, el_id):
        self.canvas.delete(el_id)