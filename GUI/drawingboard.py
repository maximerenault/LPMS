from GUI.gridzoom import GridZoom
from GUI.attributes import Attributes
from elements.node import Node
from elements.wire import Wire
from elements.resistor import Resistor
from elements.capacitor import Capacitor
from elements.inductor import Inductor
from solvers.circuitgraph import CircuitGraph
from utils.geometry import *
import tkinter as tk
from tkinter import ttk
import pickle

class DrawingBoard(GridZoom):
    def __init__(self, mainframe):
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
        self.drag_functions = ["Move", "Edit", "Wire", "R", "C", "L"]
        for fc in self.drag_functions:
            radio = tk.Radiobutton(self.frameChoices, text=fc, variable=self.radiovalue, value=fc, command=self.dragchanger).pack(side=tk.LEFT, padx=6,pady=3)
        self.drag_function = "Move"
        self.prevdragx = 0
        self.prevdragy = 0

        self.frameAttr = Attributes(self.master,self)
        self.frameAttr.grid(row=0, column=1, pady=1)
        self.selected_elem = -1

        self.frameSolve = ttk.Frame(self.master)
        self.frameSolve.grid(row=2, column=1, pady=1)
        self.solvebutton = ttk.Button(self.frameSolve, command= self.solve, text='Solve').pack(side=tk.LEFT, padx=6,pady=3)
        self.savebutton = ttk.Button(self.frameSolve, command= self.save, text='Save').pack(side=tk.LEFT, padx=6,pady=3)
        self.loadbutton = ttk.Button(self.frameSolve, command= self.load, text='Load').pack(side=tk.LEFT, padx=6,pady=3)
        self.cgraph = CircuitGraph()
    
    def dr_resize(self, event):
        '''
        Resizing the window and
        redrawing everything
        '''
        dx, dy = self.resize()
        self.canvas.move("circuit", dx, dy)

    def dr_move_from(self, event):
        '''
        Function for first press
        of left MB
        '''

        # In Edit mode, all the work is done in elem.onElemClick
        if self.drag_function == "Edit" :
            return
        
        # In Moving mode, all the work is done in gridzoom
        self.move_from(event)
        if self.drag_function == "Move" :
            return
        
        # In Drawing mode, we use geometry function to check if the start belongs to an element already defined
        # In that case the start of the new element is set at the end of the one already defined
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
            elem = Wire(node1, node2)
        elif self.drag_function == "R" :
            elem = Resistor(node1, node2, 10)
        elif self.drag_function == "C" :
            elem = Capacitor(node1, node2, 10)
        elif self.drag_function == "L" :
            elem = Inductor(node1, node2, 10)
        if self.drag_function in self.drag_func_elems :
            elem.draw(self)
            node1.add_elem(elem)
            node2.add_elem(elem)
            self.cgraph.add_elem(elem)
        print(self.cgraph.elems)

    def dr_move_to(self, event):
        '''
        Function for moving mouse
        while pressing left MB
        '''
        if self.drag_function == "Move" :
            self.canvas.move("circuit", event.x - self.prevx, event.y - self.prevy)
            self.move_to(event)
        elif self.drag_function in self.drag_func_elems :
            x1, y1 = self.pix2coord(event.x, event.y)
            x1 = round(x1)
            y1 = round(y1)
            if self.prevdragx!=x1 or self.prevdragy!=y1 :
                self.prevdragx = x1
                self.prevdragy = y1
                elem = self.cgraph.elems[-1]
                x0,y0,_,_ = elem.getcoords()
                elem.setend(x1,y1)
                for el in self.cgraph.elems[:-1]:
                    tempx, tempy = intersect(elem,el)
                    if distance(x0,y0,tempx,tempy)<=distance(x0,y0,x1,y1) :
                        x1 = tempx
                        y1 = tempy
                elem.setend(x1,y1)
                elem.redraw(self)
                self.show_frontground(event)

    def dr_release(self, event):
        '''
        Function for releasing left MB
        '''
        if self.drag_function in self.drag_func_elems :
            elem = self.cgraph.elems[-1]
            coords = elem.getcoords()
            if coords[0]==coords[2] and coords[1]==coords[3] :
                self.cgraph.del_elem(-1)
            else :
                self.cgraph.add_elem_nodes(elem)

    def dr_wheel(self, event):
        '''
        Function for rolling the
        mouse wheel
        '''
        self.gridwheel(event)
        for el in self.cgraph.elems :
            el.redraw(self)

    def dragchanger(self, event=None):
        self.drag_function = self.radiovalue.get() #selected radio value
    
    def deleteElement(self, el_id):
        el = self.cgraph.elems[el_id]
        for id in el.ids :
            self.canvas.delete(id)

    def solve(self):
        self.cgraph.gen_connx()
        self.cgraph.show()

    def save(self):
        file = open('save.pkl', 'wb')
        pickle.dump(self.cgraph, file)

    def load(self):
        file = open('save.pkl', 'rb')
        for el in self.cgraph.elems :
            for id in el.ids :
                self.canvas.delete(id)
        self.cgraph = pickle.load(file)
        for el in self.cgraph.elems :
            el.ids = []
            el.draw(self)
