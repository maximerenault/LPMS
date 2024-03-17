import numpy as np
from exceptions.elementsexceptions import *


class Wire:
    def __init__(self, node1, node2, value: float | str | None = None, active: bool = False) -> None:
        self.name = ""
        self.nameid = -1
        self.nodes = [node1, node2]
        self.bbox = -1
        self.ids = []
        self.widths = [1]

        # Useful for elements with value
        self.active = active
        self.set_value(value)

    def drawbbox(self, drbd):
        x0, y0, x1, y1, x2, y2, x3, y3 = drbd.coord2pix(self.get_bbox_coords())
        self.bbox = drbd.canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, fill="", outline="", tags="circuit")
        drbd.canvas.tag_bind(self.bbox, "<ButtonPress-1>", lambda event, drbd=drbd: self.onElemClick(event, drbd))
        drbd.canvas.tag_bind(self.bbox, "<Enter>", lambda event, drbd=drbd: self.onElemHoverI(event, drbd))
        drbd.canvas.tag_bind(self.bbox, "<Leave>", lambda event, drbd=drbd: self.onElemHoverO(event, drbd))

    def redrawbbox(self, drbd):
        x0, y0, x1, y1, x2, y2, x3, y3 = drbd.coord2pix(self.get_bbox_coords())
        drbd.canvas.coords(self.bbox, x0, y0, x1, y1, x2, y2, x3, y3)

    def drawname(self, drbd):
        x0, y0, x1, y1 = drbd.coord2pix(self.getcoords())
        x = (x0 + x1) // 2
        y = (y0 + y1) // 2
        self.nameid = drbd.canvas.create_text(x, y, text=self.name, tags="circuit")

    def redrawname(self, drbd):
        x0, y0, x1, y1 = drbd.coord2pix(self.getcoords())
        x = (x0 + x1) // 2
        y = (y0 + y1) // 2
        drbd.canvas.coords(self.nameid, x, y)
        drbd.canvas.itemconfig(self.nameid, text=self.name)

    def draw(self, drbd):
        x0, y0, x1, y1 = drbd.coord2pix(self.getcoords())
        self.ids.append(drbd.canvas.create_line(x0, y0, x1, y1, tags="circuit"))
        self.drawname(drbd)
        self.drawbbox(drbd)

    def redraw(self, drbd):
        x0, y0, x1, y1 = drbd.coord2pix(self.getcoords())
        drbd.canvas.coords(self.ids[0], x0, y0, x1, y1)
        self.redrawname(drbd)
        self.redrawbbox(drbd)

    def get_bbox_coords(self):
        coords = self.getcoords()
        vec = coords[2:] - coords[:2]
        l = np.linalg.norm(vec)
        if l == 0:
            return np.concatenate((coords, coords))
        w = 0.8 * l
        h = 0.4
        vec = vec / l
        vor = np.array([-vec[1], vec[0]])
        mid = (coords[2:] + coords[:2]) / 2
        p0 = mid - w / 2 * vec + h / 2 * vor
        p1 = mid + w / 2 * vec + h / 2 * vor
        p2 = mid + w / 2 * vec - h / 2 * vor
        p3 = mid - w / 2 * vec - h / 2 * vor
        return np.concatenate((p0, p1, p2, p3))

    def getcoords(self):
        return np.concatenate((self.nodes[0].getcoords(), self.nodes[1].getcoords()))

    def setstart(self, x, y):
        self.nodes[0].setcoords(x, y)

    def setend(self, x, y):
        self.nodes[1].setcoords(x, y)

    def onElemClick(self, event, drbd):
        if drbd.drag_function == "Edit":
            id, _ = drbd.cgraph.binary_search_elem(0, len(drbd.cgraph.elems), self)
            if _:
                drbd.frameAttr.change_elem(id)
            else:
                print("Error: Could not find element")

    def onElemHoverI(self, event, drbd):
        if drbd.drag_function == "Edit":
            for id, w in zip(self.ids, self.widths):
                drbd.canvas.itemconfig(id, width=w + 2)

    def onElemHoverO(self, event, drbd):
        if drbd.drag_function == "Edit":
            for id, w in zip(self.ids, self.widths):
                drbd.canvas.itemconfig(id, width=w)

    def delete(self, drbd):
        for id in self.ids:
            drbd.canvas.delete(id)
        drbd.canvas.delete(self.bbox)
        drbd.canvas.delete(self.nameid)

    def __str__(self):
        return "W" + str(self.ids[0])

    def __repr__(self):
        return str(self)

    def set_value(self, value):
        if not self.active and not (isinstance(value, float) or value == None):
            try:
                value = float(value)
            except:
                raise BadValueTypeError(type(value), float)
        if self.active and not (isinstance(value, str) or value == None):
            raise BadValueTypeError(type(value), str)
        self.value = value
        # source = sp.interpolate.CubicSpline(x, y, extrapolate="periodic")
        # self.source = source

    def get_value(self):
        return self.value

    def set_name(self, name: str):
        self.name = name

    def to_dict(self, nodes_list: list) -> dict:
        my_dict = {}
        my_dict["type"] = self.__class__.__name__
        my_dict["name"] = self.name
        my_dict["nodes"] = [nodes_list.index(self.nodes[0]), nodes_list.index(self.nodes[1])]
        my_dict["active"] = self.active
        my_dict["value"] = self.get_value()
        return my_dict
