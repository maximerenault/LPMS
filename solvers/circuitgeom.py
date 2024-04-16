from elements.node import Node
from elements.wire import Wire


class CircuitGeom:
    def __init__(self) -> None:
        """
        A class for circuit geometry representation for drawing.
        """
        self.elems = []
        self.nodes = []

    def add_elem(self, elem:Wire) -> None:
        self.elems.append(elem)

    def add_elem_nodes(self, elem:Wire) -> None:
        for i in range(len(elem.nodes)):
            self.nodes.append(elem.nodes[i])

    def del_elem(self, index:int) -> None:
        """
        Deletes the element at position [index].
        Also deletes associated nodes.
        """
        elem = self.elems[index]
        for i in range(len(elem.nodes)):
            if elem.nodes[i] in self.nodes:
                self.nodes.remove(elem.nodes[i])
        self.elems.remove(elem)

    ##
    # DEPREC
    ##

    def binary_search_node(self, low:int, high:int, node:Node) -> tuple[int, bool]:
        """
        Returns the index of the node for insertion,
        or the index of the existing node if exists==True.

        Actually useless because sorted+bisect does the same thing.
        """
        index = 0
        exists = False
        l = len(self.nodes)
        if l == 0:
            index = 0
            exists = False
        elif high >= low:
            mid = (high + low) // 2
            snode = self.nodes[mid]
            if snode == node:
                index = mid
                exists = True
            elif snode > node:
                return self.binary_search_node(low, mid - 1, node)
            else:
                return self.binary_search_node(mid + 1, high, node)
        else:
            index = low
            exists = False
        return index, exists

    def binary_search_elem(self, low:int, high:int, elem:Wire) -> tuple[int, bool]:
        """
        Returns the index of the elem for insertion,
        or the index of the existing elem if exists==True.
        Normally elems are created in order so there shouldn't be any use for the first option.
        """
        index = 0
        exists = False
        selems = self.elems
        l = len(selems)
        if l == 0:
            index = 0
            exists = False
        elif high >= low:
            mid = (high + low) // 2
            sid = selems[mid].ids[0]
            id = elem.ids[0]
            if sid == id:
                index = mid
                exists = True
            elif sid > id:
                return self.binary_search_elem(low, mid - 1, elem)
            else:
                return self.binary_search_elem(mid + 1, high, elem)
        else:
            index = low
            exists = False
        return index, exists