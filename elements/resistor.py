import numpy as np
from elements.wire import Wire

class Resistor(Wire):
    def __init__(self, drbd, node1, node2, R) -> None:
        super().__init__(drbd, node1, node2)
        self.R = R
    
    def draw(self):
        x0, y0, x1, y1 = self.drbd.coord2pix(self.getcoords())
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
        x0, y0, x1, y1 = self.drbd.coord2pix(self.getcoords())
        self.drbd.canvas.coords(self.ids[0], x0, y0, x1, y1)
        x0, y0, x1, y1, x2, y2, x3, y3 = self.get_rect_coords()
        x0, y0, x1, y1, x2, y2, x3, y3 = self.drbd.coord2pix(np.array([x0,y0,x1,y1,x2,y2,x3,y3]))
        self.drbd.canvas.coords(self.ids[1], x0, y0, x1, y1, x2, y2, x3, y3)

    def get_rect_coords(self):
        w = 0.6
        h = 0.3
        coords = self.getcoords()
        vec = coords[2:]-coords[:2]
        l = np.linalg.norm(vec)
        if l == 0 :
            return np.concatenate((coords,coords))
        vec = vec/l
        vor = np.array([-vec[1],vec[0]])
        mid = (coords[2:]+coords[:2])/2
        p0 = mid-w/2*vec+h/2*vor
        p1 = mid+w/2*vec+h/2*vor
        p2 = mid+w/2*vec-h/2*vor
        p3 = mid-w/2*vec-h/2*vor
        return np.concatenate((p0, p1, p2, p3))

    def __str__(self):
        return 'R'+str(self.ids[0])
    
    def __repr__(self):
        return str(self)