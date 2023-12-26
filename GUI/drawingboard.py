from GUI.gridzoom import GridZoom
from elements.node import Node
from elements.wire import Wire
from elements.resistor import Resistor
from elements.capacitor import Capacitor
from elements.inductor import Inductor
from solvers.circuitgraph import CircuitGraph
from utils.geometry import *
import tkinter as tk
from tkinter import ttk

class DrawingBoard(GridZoom):
    def __init__(self, mainframe):
        ''' Initialize the main Frame '''
        GridZoom.__init__(self, mainframe)
        # Bind events to the Canvas
        self.canvas.bind('<Configure>', self.dr_resize)  # canvas is resized
        self.canvas.bind('<ButtonPress-1>',     self.dr_move_from)
        self.canvas.bind('<ButtonRelease-1>',     self.dr_release)
        self.canvas.bind('<B1-Motion>',         self.dr_move_to)
        self.canvas.bind('<MouseWheel>', self.dr_wheel)  # with Windows and MacOS, but not Linux
        self.canvas.bind('<Button-5>',   self.dr_wheel)  # only with Linux, wheel scroll down
        self.canvas.bind('<Button-4>',   self.dr_wheel)  # only with Linux, wheel scroll up

        self.frameChoices = ttk.Frame(self.master)
        self.frameChoices.grid(row=2, column=0, pady=1)
        self.radiovalue = tk.StringVar()
        self.radiovalue.set("Move") #Default Select
        self.drag_func_elems = ["Wire", "R", "C", "L"]
        self.drag_functions = ["Move", "Wire", "R", "C", "L"]
        for fc in self.drag_functions:
            radio = tk.Radiobutton(self.frameChoices, text=fc, variable=self.radiovalue, value=fc, command=self.dragchanger).pack(side=tk.LEFT, padx=6,pady=3)
        self.drag_function = "Move"
        self.prevdragx = 0
        self.prevdragy = 0

        self.frameSolve = ttk.Frame(self.master)
        self.frameSolve.grid(row=2, column=1, pady=1)
        self.solvebutton = ttk.Button(self.frameSolve, command= self.solve, text='Solve').pack(side=tk.LEFT, padx=6,pady=3)
        self.cgraph = CircuitGraph()
    
    def dr_resize(self, event):
        dx, dy = self.resize()
        self.canvas.move("circuit", dx, dy)

    def dr_move_from(self, event):
        self.move_from(event)
        x0, y0 = self.pix2coord(self.prevx, self.prevy)
        x0 = round(x0)
        y0 = round(y0)
        for el in self.cgraph.elems[::-1] :
            if point_on_elem(el,x0,y0) :
                _,_,x0,y0 = el.getcoords()
                break
        if self.drag_function in self.drag_func_elems :
            node1 = Node(x0,y0)
            node2 = Node(x0,y0)
        if self.drag_function == "Wire" :
            elem = Wire(self, node1, node2)
        elif self.drag_function == "R" :
            elem = Resistor(self, node1, node2, 10)
        elif self.drag_function == "C" :
            elem = Capacitor(self, node1, node2, 10)
        elif self.drag_function == "L" :
            elem = Inductor(self, node1, node2, 10)
        if self.drag_function in self.drag_func_elems :
            elem.draw()
            node1.add_elem(elem)
            node2.add_elem(elem)
            self.cgraph.add_elem(elem)

    def dr_move_to(self, event):
        if self.drag_function == "Move" :
            self.canvas.move("circuit", event.x - self.prevx, event.y - self.prevy)
            self.move_to(event)
        elif self.drag_function in self.drag_func_elems :
            x1, y1 = self.pix2coord(event.x, event.y)
            x1 = round(x1)
            y1 = round(y1)
            if self.prevdragx!=x1 or self.prevdragy!=y1 :
                elem = self.cgraph.elems[-1]
                x0,y0,_,_ = elem.getcoords()
                elem.setend(x1,y1)
                tempel = elem
                for el in self.cgraph.elems[:-1]:
                    tempx, tempy = intersect(elem,el)
                    if distance(x0,y0,tempx,tempy)<=distance(x0,y0,x1,y1) :
                        x1 = tempx
                        y1 = tempy
                        tempel = el
                if point_on_elem(tempel,x1,y1) :
                    x1 = x0
                    y1 = y0
                elem.setend(x1,y1)
                elem.redraw()
                self.show_frontground(event)
            self.prevdragx = x1
            self.prevdragy = y1

    def dr_release(self, event):
        if self.drag_function in self.drag_func_elems :
            elem = self.cgraph.elems[-1]
            coords = elem.getcoords()
            if coords[0]==coords[2] and coords[1]==coords[3] :
                self.cgraph.del_elem(-1)
            else :
                self.cgraph.add_elem_nodes(elem)

    def dr_wheel(self, event):
        self.gridwheel(event)
        for el in self.cgraph.elems :
            el.redraw()

    def dragchanger(self, event=None):
        self.drag_function = self.radiovalue.get() #selected radio value
    
    def deleteElement(self, el_id):
        self.canvas.delete(el_id)

    def solve(self):
        self.cgraph.gen_connx()
        self.cgraph.show()