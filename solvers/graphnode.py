
class GraphNode():
    def __init__(self,elems) -> None:
        self.elems = elems

    def add_elem(self,elem):
        self.elems.append(elem)

    def __str__(self):
        lastr = "GN["
        for elem in self.elems :
            lastr+=str(elem)+", "
        lastr+= "]"
        return lastr
    
    def __repr__(self):
        return str(self)