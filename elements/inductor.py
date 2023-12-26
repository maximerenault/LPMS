from elements.wire import Wire
import numpy as np
import tkinter as tk

class Inductor(Wire):
    def __init__(self, drbd, node1, node2, L) -> None:
        super().__init__(drbd, node1, node2)
        self.L = L
        self.w = 0.7
        self.h = 0.3
    
    def draw(self):
        x0, y0, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6, x7, y7 = self.get_ind_coords()
        x0, y0, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6, x7, y7 = self.drbd.coord2pix(np.array([x0,y0,x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,x6,y6,x7,y7]))
        x00, y00, x10, y10 = self.drbd.coord2pix(self.getcoords())
        self.ids.append(self.drbd.canvas.create_line(x00, y00, x6, y6,
                                                    tags="circuit"))
        self.ids.append(self.drbd.canvas.create_line(x10, y10, x7, y7,
                                                    tags="circuit"))
        self.ids.append(self.drbd.canvas.create_arc(x0, y0, x1, y1,
                                                    width = 2,
                                                    activewidth=3,
                                                    tags="circuit",
                                                    style=tk.ARC,
                                                    extent = 180))
        self.ids.append(self.drbd.canvas.create_arc(x2, y2, x3, y3,
                                                    width = 2,
                                                    activewidth=3,
                                                    tags="circuit",
                                                    style=tk.ARC,
                                                    extent = 180))
        self.ids.append(self.drbd.canvas.create_arc(x4, y4, x5, y5,
                                                    width = 2,
                                                    activewidth=3,
                                                    tags="circuit",
                                                    style=tk.ARC,
                                                    extent = 180))
    
    def redraw(self):
        x0, y0, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6, x7, y7 = self.get_ind_coords()
        x0, y0, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6, x7, y7 = self.drbd.coord2pix(np.array([x0,y0,x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,x6,y6,x7,y7]))
        x00, y00, x10, y10 = self.drbd.coord2pix(self.getcoords())
        angle = int(180*self.get_ind_angle()/np.pi)
        self.drbd.canvas.coords(self.ids[0], x00, y00, x6, y6)
        self.drbd.canvas.coords(self.ids[1], x10, y10, x7, y7)
        self.drbd.canvas.coords(self.ids[2], x0, y0, x1, y1)
        self.drbd.canvas.itemconfig(self.ids[2], start = angle)
        self.drbd.canvas.coords(self.ids[3], x2, y2, x3, y3)
        self.drbd.canvas.itemconfig(self.ids[3], start = angle)
        self.drbd.canvas.coords(self.ids[4], x4, y4, x5, y5)
        self.drbd.canvas.itemconfig(self.ids[4], start = angle)

    def get_ind_coords(self):
        w = self.w
        h = self.h
        coords = self.getcoords()
        vec = coords[2:]-coords[:2]
        l = np.linalg.norm(vec)
        if l == 0 :
            return np.concatenate((coords,coords,coords,coords))
        vec = vec/l
        mid = (coords[2:]+coords[:2])/2
        ce1 = mid-w/3*vec
        ce2 = mid
        ce3 = mid+w/3*vec
        diag = np.array([-w/6,w/6])
        p0 = ce1 + diag
        p1 = ce1 - diag
        p2 = ce2 + diag
        p3 = ce2 - diag
        p4 = ce3 + diag
        p5 = ce3 - diag
        p6 = mid-w/2*vec
        p7 = mid+w/2*vec
        return np.concatenate((p0, p1, p2, p3, p4, p5, p6, p7))
    
    def get_ind_angle(self):
        x0, y0, x1, y1 = self.getcoords()
        if x1 == x0 :
            return -np.pi/2
        angle = np.arctan((y1-y0)/(x1-x0))
        return angle

    def __str__(self):
        return 'L'+str(self.ids[0])
    
    def __repr__(self):
        return str(self)