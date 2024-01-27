
class CircuitSolver():
    def __init__(self, elems, nodes) -> None:
        self.elems = elems
        self.nodes = nodes
        self.circAmat = []
        self.circBvec = []

    def buildAmat(self) -> None:
        pass