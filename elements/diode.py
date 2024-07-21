import numpy as np
from elements.wire import Wire


class Diode(Wire):
    def __init__(self, node1, node2, value: None = None, active: bool = False) -> None:
        super().__init__(node1, node2, value, active)
        self.widths = [1, 2, 2]

    def draw(self, drbd):
        x0, y0, x1, y1 = drbd.coord2pix(self.getcoords())
        self.ids.append(drbd.canvas.create_line(x0, y0, x1, y1, tags="circuit"))
        x0, y0, x1, y1, x2, y2, x3, y3, x4, y4 = drbd.coord2pix(self.get_diode_coords())
        self.ids.append(
            drbd.canvas.create_polygon(
                x0, y0, x1, y1, x2, y2, fill="white", outline="black", width=2, tags="circuit"
            )
        )
        self.ids.append(drbd.canvas.create_line(x3, y3, x4, y4, width=2, tags="circuit"))
        self.afterdraw(drbd)

    def redraw(self, drbd):
        x0, y0, x1, y1 = drbd.coord2pix(self.getcoords())
        drbd.canvas.coords(self.ids[0], x0, y0, x1, y1)
        x0, y0, x1, y1, x2, y2, x3, y3, x4, y4 = drbd.coord2pix(self.get_diode_coords())
        drbd.canvas.coords(self.ids[1], x0, y0, x1, y1, x2, y2)
        drbd.canvas.coords(self.ids[2], x3, y3, x4, y4)
        self.afterredraw(drbd)

    def get_diode_coords(self):
        w = 0.38
        h = 0.45
        coords = self.getcoords()
        vec = coords[2:] - coords[:2]
        l = np.linalg.norm(vec)
        if l == 0:
            return np.concatenate((coords, coords, coords[0:2]))
        vec = vec / l
        vor = np.array([-vec[1], vec[0]])
        mid = (coords[2:] + coords[:2]) / 2
        p0 = mid - w / 2 * vec + h / 2 * vor
        p1 = mid + w / 2 * vec
        p2 = mid - w / 2 * vec - h / 2 * vor
        p3 = mid + w / 2 * vec + h / 2 * vor
        p4 = mid + w / 2 * vec - h / 2 * vor
        return np.concatenate((p0, p1, p2, p3, p4))

    def __str__(self):
        return "D" + str(self.ids[0])

    def __repr__(self):
        return str(self)
