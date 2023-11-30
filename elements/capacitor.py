from elements.wire import Wire
import numpy as np

class Capacitor(Wire):
    def __init__(self, drbd, x0, y0, x1, y1, C) -> None:
        super().__init__(drbd, x0, y0, x1, y1)
        self.C = C
        self.w = 0.2
        self.h = 0.6
    
    def draw(self):
        x0, y0, x1, y1, x2, y2, x3, y3 = self.get_cap_coords()
        x01 = (x0+x3)/2
        y01 = (y0+y3)/2
        x11 = (x1+x2)/2
        y11 = (y1+y2)/2
        x0, y0, x1, y1, x2, y2, x3, y3 = self.drbd.coord2pix(np.array([x0,y0,x1,y1,x2,y2,x3,y3]))
        self.ids.append(self.drbd.canvas.create_line(x0, y0, x3, y3,
                                                    tags="circuit"))
        self.ids.append(self.drbd.canvas.create_line(x1, y1, x2, y2,
                                                    tags="circuit"))
        
        x01, y01, x11, y11 = self.drbd.coord2pix(np.array([x01,y01,x11,y11]))
        x00, y00, x10, y10 = self.drbd.coord2pix(self.coords)
        self.ids.append(self.drbd.canvas.create_line(x00, y00, x01, y01,
                                                    tags="circuit"))
        self.ids.append(self.drbd.canvas.create_line(x10, y10, x11, y11,
                                                    tags="circuit"))
    
    def redraw(self):
        x0, y0, x1, y1, x2, y2, x3, y3 = self.get_cap_coords()
        x01 = (x0+x3)/2
        y01 = (y0+y3)/2
        x11 = (x1+x2)/2
        y11 = (y1+y2)/2
        x0, y0, x1, y1, x2, y2, x3, y3 = self.drbd.coord2pix(np.array([x0,y0,x1,y1,x2,y2,x3,y3]))
        self.drbd.canvas.coords(self.ids[0], x0, y0, x3, y3)
        self.drbd.canvas.coords(self.ids[1], x1, y1, x2, y2)

        x01, y01, x11, y11 = self.drbd.coord2pix(np.array([x01,y01,x11,y11]))
        x00, y00, x10, y10 = self.drbd.coord2pix(self.coords)
        self.drbd.canvas.coords(self.ids[2], x00, y00, x01, y01)
        self.drbd.canvas.coords(self.ids[3], x10, y10, x11, y11)

    def get_cap_coords(self):
        w = self.w
        h = self.h
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