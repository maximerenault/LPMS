import numpy as np
from elements.wire import Wire

class Resistor(Wire):
    def __init__(self, drbd, x0, y0, x1, y1, R) -> None:
        super().__init__(drbd, x0, y0, x1, y1)
        self.R = R
    
    def draw(self):
        x0, y0, x1, y1 = self.drbd.coord2pix(self.coords)
        self.ids.append(self.drbd.canvas.create_line(x0, y0, x1, y1,
                                                    tags="circuit"))
        x0, y0, x1, y1, x2, y2, x3, y3 = self.get_rect_coords()
        x0, y0, x1, y1, x2, y2, x3, y3 = self.drbd.coord2pix(np.array([x0,y0,x1,y1,x2,y2,x3,y3]))
        self.ids.append(self.drbd.canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, 
                                                        fill="white",
                                                        outline="black",
                                                        width = 2,
                                                        activewidth=3,
                                                        tags="circuit"))
    
    def redraw(self):
        x0, y0, x1, y1 = self.drbd.coord2pix(self.coords)
        self.drbd.canvas.coords(self.ids[0], x0, y0, x1, y1)
        x0, y0, x1, y1, x2, y2, x3, y3 = self.get_rect_coords()
        x0, y0, x1, y1, x2, y2, x3, y3 = self.drbd.coord2pix(np.array([x0,y0,x1,y1,x2,y2,x3,y3]))
        self.drbd.canvas.coords(self.ids[1], x0, y0, x1, y1, x2, y2, x3, y3)

    def get_rect_coords(self):
        w = 0.6
        h = 0.4
        vec = self.coords[2:]-self.coords[:2]
        l = np.linalg.norm(vec)
        if l == 0 :
            return np.concatenate((self.coords,self.coords))
        vec = vec/l
        vor = np.array([-vec[1],vec[0]])
        mid = (self.coords[2:]+self.coords[:2])/2
        p0 = mid-w/2*vec+h/2*vor
        p1 = mid+w/2*vec+h/2*vor
        p2 = mid+w/2*vec-h/2*vor
        p3 = mid-w/2*vec-h/2*vor
        return np.concatenate((p0, p1, p2, p3))