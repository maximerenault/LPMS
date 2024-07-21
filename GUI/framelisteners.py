from tkinter import ttk
import tkinter as tk
from elements.node import Node
from elements.wire import Wire


class FrameListeners(ttk.Treeview):

    def __init__(self, master, drbd):
        super().__init__(master)
        self.heading("#0", text="Listener names")
        self.insert("", 0, "P", text="Pressure")
        self.insert("", 1, "Q", text="Flow")
        self.bind("<Double-1>", self.on_double_click)
        self.bind("<Motion>", self.on_motion)
        self.on_motion_activated = True
        self.drbd = drbd
        self.last_focus = ""
        self.cQ = 0
        self.cP = 0
        self.Plisteners = {}
        self.Qlisteners = {}

    def add_pressure_listener(self, node: Node):
        P = "P" + str(self.cP)
        if node.listener_name == "":
            Ptxt = P
        else:
            Ptxt = node.listener_name
        self.cP += 1
        self.insert("P", index=tk.END, iid=P, text=Ptxt)
        self.Plisteners[node.id] = P
        self.Plisteners[P] = node
        node.listener_name = Ptxt

    def remove_pressure_listener(self, node: Node):
        if node.id in self.Plisteners:
            P = self.Plisteners[node.id]
            self.delete(P)
            del self.Plisteners[node.id]
            del self.Plisteners[P]

    def add_flow_listener(self, elem: Wire):
        Q = "Q" + str(self.cQ)
        if elem.listener_name == "":
            Qtxt = Q
        else:
            Qtxt = elem.listener_name
        self.cQ += 1
        self.insert("Q", index=tk.END, iid=Q, text=Qtxt)
        self.Qlisteners[elem.ids[0]] = Q
        self.Qlisteners[Q] = elem
        elem.listener_name = Qtxt

    def remove_flow_listener(self, elem: Wire):
        if elem.ids[0] in self.Qlisteners:
            Q = self.Qlisteners[elem.ids[0]]
            self.delete(Q)
            del self.Qlisteners[elem.ids[0]]
            del self.Qlisteners[Q]

    def on_double_click(self, event):
        self.on_motion_activated = False
        elem_iid = self.focus()
        if elem_iid in ["P", "Q"]:
            return
        param_dic = self.item(elem_iid)
        elem_text = param_dic["text"]
        bbox = self.bbox(elem_iid)
        entry_edit = ttk.Entry(self)
        entry_edit.insert(0, elem_text)
        entry_edit.select_range(0, tk.END)
        entry_edit.focus()
        entry_edit.bind("<FocusOut>", self.on_focus_out)
        entry_edit.bind("<Return>", lambda e, iid=elem_iid: self.on_enter_press(e, iid))
        entry_edit.place(x=bbox[0], y=bbox[1], w=bbox[2], h=bbox[3])

    def on_focus_out(self, event):
        self.on_motion_activated = True
        event.widget.destroy()

    def on_enter_press(self, event, iid):
        new_text = event.widget.get()
        self.edit_listener(iid, new_text)
        self.on_motion_activated = True
        event.widget.destroy()

    def edit_listener(self, iid, text):
        if iid == "":
            return
        elem_parent = self.parent(iid)
        if elem_parent == "P":
            node = self.Plisteners[iid]
            node.listener_name = text
        if elem_parent == "Q":
            elem = self.Qlisteners[iid]
            elem.listener_name = text
        self.item(iid, text=text)

    def get_elem_iid(self, elem):
        try:
            return self.Qlisteners[elem]
        except:
            return ""

    def get_node_iid(self, node):
        try:
            return self.Plisteners[node]
        except:
            return ""
        
    def on_motion(self, event):
        if not self.on_motion_activated:
            return
        iid = self.identify_row(event.y)
        if self.last_focus != iid :
            self.focus(iid)
            self.selection_set(iid)
            self.leave_listener(self.last_focus)
            self.enter_listener(iid)
            self.last_focus = iid

    def enter_listener(self, iid):
        if iid == "":
            return
        elem_parent = self.parent(iid)
        if elem_parent == "P":
            node = self.Plisteners[iid]
            node.radius += 0.1
            node.redraw(self.drbd)
        if elem_parent == "Q":
            elem = self.Qlisteners[iid]
            elem.Qsize = 2.0
            elem.redraw(self.drbd)

    def leave_listener(self, iid):
        if iid == "":
            return
        elem_parent = self.parent(iid)
        if elem_parent == "P":
            node = self.Plisteners[iid]
            node.radius -= 0.1
            node.redraw(self.drbd)
        if elem_parent == "Q":
            elem = self.Qlisteners[iid]
            elem.Qsize = 1.0
            elem.redraw(self.drbd)

    def reinitialize(self):
        self.cQ = 0
        self.cP = 0
        for id in self.Plisteners:
            P = self.Plisteners[id]
            self.delete(P)
        for id in self.Qlisteners:
            Q = self.Qlisteners[id]
            self.delete(Q)
        self.Plisteners = {}
        self.Qlisteners = {}
