import numpy as np

class Wire():
    def __init__(self, drbd, x0, y0, x1, y1) -> None:
        self.drbd = drbd
        self.coords = np.array([x0, y0, x1, y1])
        self.ids = []
    
    def draw(self):
        x0, y0, x1, y1 = self.drbd.coord2pix(self.coords)
        self.ids.append(self.drbd.canvas.create_line(x0, y0, x1, y1,
                                                     activewidth=3,
                                                     tags="circuit"))
    
    def redraw(self):
        x0, y0, x1, y1 = self.drbd.coord2pix(self.coords)
        self.drbd.canvas.coords(self.ids[0], x0, y0, x1, y1)