import numpy as np
import json

class Wire():
    def __init__(self, node1, node2) -> None:
        self.name = ''
        self.nodes = [node1, node2]
        self.bbox = -1
        self.ids = []
        self.widths = [1]
    
    def drawbbox(self, drbd):
        x0, y0, x1, y1, x2, y2, x3, y3 = self.get_bbox_coords()
        x0, y0, x1, y1, x2, y2, x3, y3 = drbd.coord2pix(np.array([x0,y0,x1,y1,x2,y2,x3,y3]))
        self.bbox = drbd.canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, 
                                                    fill="",
                                                    outline="",
                                                    tags="circuit")
        drbd.canvas.tag_bind(self.bbox, '<ButtonPress-1>', lambda event,drbd=drbd : self.onElemClick(event,drbd))
        drbd.canvas.tag_bind(self.bbox, '<Enter>', lambda event,drbd=drbd : self.onElemHoverI(event,drbd))
        drbd.canvas.tag_bind(self.bbox, '<Leave>', lambda event,drbd=drbd : self.onElemHoverO(event,drbd))

    def redrawbbox(self, drbd):
        x0, y0, x1, y1, x2, y2, x3, y3 = self.get_bbox_coords()
        x0, y0, x1, y1, x2, y2, x3, y3 = drbd.coord2pix(np.array([x0,y0,x1,y1,x2,y2,x3,y3]))
        drbd.canvas.coords(self.bbox, x0, y0, x1, y1, x2, y2, x3, y3)

    def draw(self, drbd):
        x0, y0, x1, y1 = drbd.coord2pix(self.getcoords())
        self.ids.append(drbd.canvas.create_line(x0, y0, x1, y1,
                                                # activewidth=3,
                                                tags="circuit"))
        self.drawbbox(drbd)
    
    def redraw(self, drbd):
        x0, y0, x1, y1 = drbd.coord2pix(self.getcoords())
        drbd.canvas.coords(self.ids[0], x0, y0, x1, y1)
        self.redrawbbox(drbd)

    def getcoords(self):
        return np.concatenate((self.nodes[0].getcoords(), self.nodes[1].getcoords()))

    def get_bbox_coords(self):
        coords = self.getcoords()
        vec = coords[2:]-coords[:2]
        l = np.linalg.norm(vec)
        if l == 0 :
            return np.concatenate((coords,coords))
        w = 0.8*l
        h = 0.4
        vec = vec/l
        vor = np.array([-vec[1],vec[0]])
        mid = (coords[2:]+coords[:2])/2
        p0 = mid-w/2*vec+h/2*vor
        p1 = mid+w/2*vec+h/2*vor
        p2 = mid+w/2*vec-h/2*vor
        p3 = mid-w/2*vec-h/2*vor
        return np.concatenate((p0, p1, p2, p3))
    
    def setend(self,x,y):
        self.nodes[1].setcoords(x,y)

    def onElemClick(self, event, drbd):
        if drbd.drag_function == "Edit" :
            id, _ = drbd.cgraph.binary_search_elem(0,len(drbd.cgraph.elems),self)
            if _ :
                drbd.frameAttr.change_elem(id)
            else :
                print("Error: Could not find element")
    
    def onElemHoverI(self, event, drbd):
        if drbd.drag_function == "Edit" :
            for id,w in zip(self.ids,self.widths) :
                drbd.canvas.itemconfig(id,width=w+2)
    
    def onElemHoverO(self, event, drbd):
        if drbd.drag_function == "Edit" :
            for id,w in zip(self.ids,self.widths) :
                drbd.canvas.itemconfig(id,width=w)

    def __str__(self):
        return 'W'+str(self.ids[0])
    
    def __repr__(self):
        return str(self)