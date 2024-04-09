import numpy as np
from functools import total_ordering 
  
@total_ordering
class Node:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        self.elems = []

    def getcoords(self):
        return np.array([self.x, self.y])

    def setcoords(self, x, y):
        self.x = x
        self.y = y

    def add_elem(self, elem):
        self.elems.append(elem)
  
    def __lt__(self, node):
        return (self.x < node.x or (self.x == node.x and self.y < node.y))
  
    def __gt__(self, node):
        return (self.x > node.x or (self.x == node.x and self.y > node.y))
  
    def __le__(self, node):
        return (self.x < node.x or (self.x == node.x and self.y <= node.y))
  
    def __ge__(self, node):
        return (self.x > node.x or (self.x == node.x and self.y >= node.y))
  
    def __eq__(self, node): 
        return (self.x == node.x and self.y == node.y)

    def __str__(self):
        return "N[" + str(self.x) + ", " + str(self.y) + "]"

    def __repr__(self):
        return str(self)

    def to_dict(self):
        return [float(self.x), float(self.y)]
