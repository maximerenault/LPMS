from tkinter import ttk
import tkinter as tk

class Attributes(ttk.Frame):
    """
    A class for displaying info about an element
    and editing it
    """
    def __init__(self, master, drbd):
        ttk.Frame.__init__(self, master)
        self.namebox = tk.Entry(self, width = 10, bg = "light yellow", state=tk.DISABLED)
        self.namebox.grid(row=0, column=0, sticky='we')
        self.namebox.bind('<Return>', self.update_name)

        self.startbox = tk.Entry(self, width = 10, bg = "light blue", state=tk.DISABLED)
        self.startbox.grid(row=1, column=0, sticky='we')
        self.startbox.bind('<Return>', self.update_start)

        self.endbox = tk.Entry(self, width = 10, bg = "light blue", state=tk.DISABLED)
        self.endbox.grid(row=2, column=0, sticky='we')
        self.endbox.bind('<Return>', self.update_end)

        status = tk.StringVar()
        status.set("Press Enter to validate")
        self.instructions = tk.Label(self, textvariable=status)
        self.instructions.grid(row=3, column=0, sticky='we')

        self.deletebutton = ttk.Button(self, command= self.delete_elem, text='Delete', state=tk.DISABLED)
        self.deletebutton.grid(row=4, column=0, sticky='we')
        self.drbd = drbd
        self.elem = -1

    def update_name(self, event):
        if self.elem == -1 :
            self.clean_all()
            self.disable_all()
            return
        el = self.drbd.cgraph.elems[self.elem]
        el.name = self.namebox.get()
        el.redrawname(self.drbd)
        
    def update_start(self, event):
        if self.elem == -1 :
            self.clean_all()
            self.disable_all()
            return
        el = self.drbd.cgraph.elems[self.elem]
        xy = self.startbox.get()
        xy = xy.split(",")
        x = int(xy[0])
        y = int(xy[1])
        el.nodes[0].setcoords(x,y)
        el.redraw(self.drbd)
        
    def update_end(self, event):
        if self.elem == -1 :
            self.clean_all()
            self.disable_all()
            return
        el = self.drbd.cgraph.elems[self.elem]
        xy = self.endbox.get()
        xy = xy.split(",")
        x = int(xy[0])
        y = int(xy[1])
        el.nodes[1].setcoords(x,y)
        el.redraw(self.drbd)

    def delete_elem(self):
        if self.elem == -1 :
            self.clean_all()
            self.disable_all()
            return
        self.drbd.deleteElement(self.elem)
        self.elem = -1
        self.clean_all()
        self.disable_all()

    def change_elem(self, id):
        self.elem = id
        if self.elem == -1 :
            self.clean_all()
            self.disable_all()
            return
        self.enable_all()
        self.clean_all()
        self.insert_all()

    def insert_all(self):
        el = self.drbd.cgraph.elems[self.elem]
        self.namebox.insert(tk.END,el.name)
        coords = el.getcoords()
        self.startbox.insert(tk.END,str(coords[0])+','+str(coords[1]))
        self.endbox.insert(tk.END,str(coords[2])+','+str(coords[3]))

    def clean_all(self):
        self.namebox.delete(0,tk.END)
        self.startbox.delete(0,tk.END)
        self.endbox.delete(0,tk.END)

    def enable_all(self):
        self.namebox.config(state=tk.NORMAL)
        self.startbox.config(state=tk.NORMAL)
        self.endbox.config(state=tk.NORMAL)
        self.deletebutton.config(state=tk.NORMAL)

    def disable_all(self):
        self.namebox.config(state=tk.DISABLED)
        self.startbox.config(state=tk.DISABLED)
        self.endbox.config(state=tk.DISABLED)
        self.deletebutton.config(state=tk.DISABLED)