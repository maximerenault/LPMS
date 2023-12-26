import numpy as np

class Wire():
    def __init__(self, drbd, node1, node2) -> None:
        self.drbd = drbd
        self.nodes = [node1, node2]
        self.ids = []
    
    def draw(self):
        x0, y0, x1, y1 = self.drbd.coord2pix(self.getcoords())
        self.ids.append(self.drbd.canvas.create_line(x0, y0, x1, y1,
                                                     activewidth=3,
                                                     tags="circuit"))
    
    def redraw(self):
        x0, y0, x1, y1 = self.drbd.coord2pix(self.getcoords())
        self.drbd.canvas.coords(self.ids[0], x0, y0, x1, y1)

    def getcoords(self):
        return np.concatenate((self.nodes[0].getcoords(), self.nodes[1].getcoords()))
    
    def setend(self,x,y):
        self.nodes[1].setcoords(x,y)

    def __str__(self):
        return 'W'+str(self.ids[0])
    
    def __repr__(self):
        return str(self)