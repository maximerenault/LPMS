import numpy as np
from elements.ground import Ground
import tkinter as tk


class PSource(Ground):
    def __init__(self, node1, node2, P) -> None:
        super().__init__(node1, node2)
        self.source = P
        self.period = 1.0
        self.widths = [1, 2]

    def draw(self, drbd):
        xs, ys, xe, ye, x1, y1, x2, y2 = drbd.coord2pix(self.get_psource_coords())
        self.ids.append(drbd.canvas.create_line(xs, ys, xe, ye, tags="circuit"))
        self.ids.append(drbd.canvas.create_oval(x1, y1, x2, y2, width=2, tags="circuit"))
        self.drawname(drbd)
        self.drawbbox(drbd)

    def redraw(self, drbd):
        xs, ys, xe, ye, x1, y1, x2, y2 = drbd.coord2pix(self.get_psource_coords())
        drbd.canvas.coords(self.ids[0], xs, ys, xe, ye)
        drbd.canvas.coords(self.ids[1], x1, y1, x2, y2)
        self.redrawname(drbd)
        self.redrawbbox(drbd)

    def get_psource_coords(self):
        coords = self.getcoords()
        vec = coords[2:] - coords[:2]
        l = np.linalg.norm(vec)
        if l == 0:
            vec = np.array([0, -1])
            l = 1
        vec = vec / l
        w = 0.5
        h = 0.5
        vor = np.array([-vec[1], vec[0]])
        mid = coords[:2] + vec / 2
        p0 = coords[:2]
        p1 = mid - w / 2 * vec
        diagx = np.array([1, 0])
        diagy = np.array([0, 1])
        p2 = mid - w / 2 * diagx - h / 2 * diagy
        p3 = mid + w / 2 * diagx + h / 2 * diagy
        return np.concatenate((p0, p1, p2, p3))

    def set_source(self, source):
        self.source = source

    def get_source(self):
        return self.source

    def set_period(self, period: float):
        self.period = period

    def get_period(self):
        return self.period

    def __str__(self):
        return "PSc" + str(self.ids[0])

    def __repr__(self):
        return str(self)
