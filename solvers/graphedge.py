from solvers.graphnode import GraphNode


class GraphEdge:
    def __init__(self, start: GraphNode, end: GraphNode, type:str="R", value:float=1.0) -> None:
        self.start = start
        self.end = end
        self.type = type
        self.value = value

    def __str__(self):
        lastr = "GE["+str(self.start)+","+str(self.end)+"]"
        return lastr

    def __repr__(self):
        return str(self)
