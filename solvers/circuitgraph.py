from pathlib import Path
from elements.node import Node
from elements.wire import Wire
from elements.resistor import Resistor
from elements.inductor import Inductor
from elements.capacitor import Capacitor
from elements.ground import Ground
from elements.psource import PSource
import numpy as np
from scipy.sparse.csgraph import connected_components
from scipy.sparse import csr_matrix


class CircuitGraph:
    def __init__(self) -> None:
        """
        A class that mixes geometry and graph representation
        The first for drawing, the second for solving
        """
        self.elems = []
        self.nodes = []
        self.graphnodes = []
        self.graphedges = []
        self.connectivities = []
        self.conn_mat = None
        self.elem_num = {
            Wire: 1,
            Resistor: 2,
            Inductor: 3,
            Capacitor: 4,
            Ground: 5,
            PSource: 6
        }

    def add_elem(self, elem) -> None:
        self.elems.append(elem)

    def add_elem_nodes(self, elem) -> None:
        """
        Uses a binary search to insert new nodes
        in nodes list, or to find existing nodes.
        """
        for i in range(len(elem.nodes)):
            index, exists = self.binary_search_node(0, len(self.nodes) - 1, elem.nodes[i])
            if exists:
                for el in elem.nodes[i].elems:
                    self.nodes[index].add_elem(el)
                elem.nodes[i] = self.nodes[index]
            else:
                self.nodes.insert(index, elem.nodes[i])

    def gen_connx(self) -> None:
        """
        Generates compact connectivity list
        based on elements and nodes.
        Rewrites entire connectivities.
        """
        n = len(self.nodes)
        self.connectivities = [0] * (n * (n - 1) // 2)
        for el_id in range(len(self.elems)):
            elem = self.elems[el_id]
            if isinstance(elem, Ground):
                continue
            node1 = elem.nodes[0]
            node2 = elem.nodes[1]
            con1, _ = self.binary_search_node(0, len(self.nodes) - 1, node1)
            con2, _ = self.binary_search_node(0, len(self.nodes) - 1, node2)
            n = max(con1, con2)
            m = min(con1, con2)
            self.connectivities[n * (n - 1) // 2 + m] = self.elem_num[type(elem)]
        self.conn_mat, conn_comp = self.connect2mat()
        return conn_comp

    def connect2mat(self) -> tuple[np.ndarray, int]:
        """
        Returns the full connectivity matrix
        from the compact version : connectivities.
        """
        l = len(self.nodes)
        mat = np.zeros((l, l), dtype=int)
        for i in range(l):
            for j in range(l):
                if i == j:
                    continue
                n = max(i, j)
                m = min(i, j)
                mat[i, j] = self.connectivities[n * (n - 1) // 2 + m]
        newarr = csr_matrix(mat)
        conn_comp = connected_components(newarr)[0]
        if conn_comp > 1 :
            print("Error: too many connected components: ", conn_comp)
        return mat, conn_comp

    def show(self) -> None:
        return

    def binary_search_node(self, low, high, node) -> tuple[int, bool]:
        """
        Returns the index of the node for insertion,
        or the index of the existing node if exists==True.
        """
        index = 0
        exists = False
        snodes = self.nodes
        l = len(snodes)
        if l == 0:
            index = 0
            exists = False
        elif high >= low:
            mid = (high + low) // 2
            scoords = snodes[mid].getcoords()
            coords = node.getcoords()
            if (scoords == coords).all():
                index = mid
                exists = True
            elif scoords[0] > coords[0]:
                return self.binary_search_node(low, mid - 1, node)
            elif scoords[0] == coords[0] and scoords[1] > coords[1]:
                return self.binary_search_node(low, mid - 1, node)
            else:
                return self.binary_search_node(mid + 1, high, node)
        else:
            index = low
            exists = False
        return index, exists

    def binary_search_elem(self, low, high, elem) -> tuple[int, bool]:
        """
        Returns the index of the elem for insertion,
        or the index of the existing elem if exists==True.
        Normally elems are created in order so there shouldn't be any use for the firt option.
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

    def del_elem(self, index) -> None:
        """
        Deletes the element at position [index].
        Also deletes associated nodes if they are
        not used anymore.
        """
        elem = self.elems[index]
        for i in range(2):
            index, exists = self.binary_search_node(0, len(self.nodes) - 1, elem.nodes[i])
            if exists and elem in self.nodes[index].elems:
                self.nodes[index].elems.remove(elem)
                l = len(self.nodes[index].elems)
                if l == 0:  # If node has no connection, it can be deleted
                    self.nodes.pop(index)
        self.elems.remove(elem)

    def max_len_non_branching_paths(self) -> tuple[list, list]:
        """
        Naive algorithm for maximal non-branching paths in
        a graph from : https://rosalind.info/problems/ba3m/

        Basic principle : starts from any node not in the middle
        of a path (not 2 connexions) and finds all non-branching
        paths from here.

        It is adapted here naively for non directional graph
        by removing redundancy afterwards.

        Also returns start and end of each path.
        """
        Paths = []
        StartEnds = []
        for node in self.nodes:
            if len(node.elems) != 2:
                for elem in node.elems:
                    startend = []
                    startend.append(node)
                    non_branching_path = []
                    non_branching_path.append(elem)
                    for n in elem.nodes:
                        if n is not node:
                            node1 = n
                            break
                    prevelem = elem
                    k = 0
                    while len(node1.elems) == 2:
                        for e in node1.elems:
                            if prevelem is not e:
                                non_branching_path.append(e)
                                break
                        prevelem = non_branching_path[-1]
                        for n in prevelem.nodes:
                            if n is not node1:
                                node1 = n
                                break
                        k += 1
                        if k == 10000:
                            print("Error in branching path ", node1)
                            return
                    startend.append(node1)
                    Paths.append(non_branching_path)
                    StartEnds.append(startend)
        # Delete duplicates
        rem = []
        for i in range(len(Paths) - 1):
            path = Paths[i]
            path.reverse()
            if path in Paths[i + 1 :]:
                rem.append(i)
        rem.reverse()
        for i in rem:
            del Paths[i]
            del StartEnds[i]
        for path in Paths:
            path.reverse()
        return Paths, StartEnds
    
    def build_graph(self, elem):
        return

    ######################
    # DEPRECATED METHODS
    ######################

    def gen_connectivities(self) -> None:
        """
        DEPRECATED
        Generates compact connectivities list
        based on elements coordinates.
        Rewrites entire nodes and connectivities.
        """
        self.nodes = []
        self.connectivities = []
        for el_id in range(len(self.elems)):
            elem = self.elems[el_id]
            coords = elem.getcoords()
            con1 = -1
            con2 = -1
            for i in range(len(self.nodes)):
                node = self.nodes[i]
                if (coords[:2] == node.coords).all():
                    con1 = i
                if (coords[2:] == node.coords).all():
                    con2 = i

            nb_new = 0
            if con1 == -1:
                self.nodes.append(Node(coords[0], coords[1]))
                con1 = len(self.nodes) - 1
                nb_new += 1
            if con2 == -1:
                self.nodes.append(Node(coords[2], coords[3]))
                con2 = len(self.nodes) - 1
                nb_new += 1

            n = max(con1, con2)
            m = min(con1, con2)
            if nb_new == 0:
                self.connectivities[n * (n - 1) // 2 + m] = el_id + 1
            if nb_new == 1:
                for i in range(len(self.nodes) - 1):
                    self.connectivities.append(0)
                self.connectivities[n * (n - 1) // 2 + m] = el_id + 1
            if nb_new == 2:
                for i in range(2 * len(self.nodes) - 3):
                    self.connectivities.append(0)
                self.connectivities[n * (n - 1) // 2 + m] = el_id + 1
        # print(self.connect2mat())
