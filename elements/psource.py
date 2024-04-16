import numpy as np
import scipy as sp
from elements.ground import Ground
from elements.node import Node


class PSource(Ground):
    def __init__(self, node1: Node, node2: Node, value: float | str | None = None, active: bool = False) -> None:
        super().__init__(node1, node2, value, active)
        self.name = "P"
        self.widths = [1, 2]

    def draw(self, drbd):
        xs, ys, xe, ye, x1, y1, x2, y2 = drbd.coord2pix(self.get_psource_coords())
        self.ids.append(drbd.canvas.create_line(xs, ys, xe, ye, width=self.widths[0], tags="circuit"))
        self.ids.append(drbd.canvas.create_oval(x1, y1, x2, y2, width=self.widths[1], tags="circuit"))
        self.afterdraw(drbd)

    def redraw(self, drbd):
        xs, ys, xe, ye, x1, y1, x2, y2 = drbd.coord2pix(self.get_psource_coords())
        drbd.canvas.coords(self.ids[0], xs, ys, xe, ye)
        drbd.canvas.coords(self.ids[1], x1, y1, x2, y2)
        self.afterredraw(drbd)

    def get_psource_coords(self):
        coords = self.getcoords()
        vec = coords[2:] - coords[:2]
        l = np.linalg.norm(vec)
        if l == 0:
            return np.concatenate((coords[:2], coords[:2], coords[:2], coords[:2]))
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

    # def set_value(self, x: np.ndarray, y: np.ndarray):
    #     self.value = np.array([x, y])
    #     source = sp.interpolate.CubicSpline(x, y, extrapolate="periodic")
    #     self.source = source

    # def get_value(self):
    #     return self.value

    # def set_source(self, source: function):
    #     self.source = source

    # def get_source(self):
    #     return self.source

    def __str__(self):
        return "PSc" + str(self.ids[0])

    def __repr__(self):
        return str(self)
