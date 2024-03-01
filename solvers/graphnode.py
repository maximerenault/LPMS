from solvers.graphedge import GraphEdge


types = ["Normal","Source"]

class GraphNode:
    def __init__(self, type:str="Normal") -> None:
        self.edges = []
        self.type = type

    def add_edge(self, edge:GraphEdge):
        self.edges.append(edge)

    def __str__(self):
        lastr = "GN["
        for edge in self.edges:
            lastr += str(edge) + ", "
        lastr += "]"
        return lastr

    def __repr__(self):
        return str(self)
