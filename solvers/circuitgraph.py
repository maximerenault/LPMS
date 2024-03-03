import math
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
from solvers.graphedge import GraphEdge

from solvers.graphnode import GraphNode


class CircuitGraph:
    def __init__(self) -> None:
        """
        A class that mixes geometry and graph representation
        The first for drawing, the second for solving

        It is a very convoluted representation that could
        probably be improved (meaning simplified) but it would
        take a whole redesign of the element classes and methods
        """
        self.elems = []
        self.nodes = []
        self.connectivities = []
        self.conn_mat = None
        self.elids_mat = None
        self.graph_nodes = []
        self.graph_edges = []
        self.graph_conn_mat = None
        self.graph_elids_mat = None
        self.elem_num = {Wire: 1, Resistor: 2, Inductor: 3, Capacitor: 4, Ground: 5, PSource: 6}

    def add_elem(self, elem) -> None:
        self.elems.append(elem)

    def add_elem_nodes(self, elem) -> None:
        """
        Uses a binary search to insert new nodes
        in nodes list, or to find existing nodes
        """
        for i in range(len(elem.nodes)):
            index, exists = self.binary_search_node(0, len(self.nodes) - 1, elem.nodes[i])
            if exists:
                for el in elem.nodes[i].elems:
                    self.nodes[index].add_elem(el)
                elem.nodes[i] = self.nodes[index]
            else:
                self.nodes.insert(index, elem.nodes[i])

    def pre_solve(self) -> int:
        """
        Takes the steps needed to build graph
        nodes and edges readable by the class
        CircuitSolver
        """
        conn_comp = self.gen_connx()
        self.build_graph_conn_mat()
        self.build_graph_nodes_edges()
        return conn_comp

    def gen_connx(self) -> int:
        """
        Generates compact connectivity list
        based on elements and nodes

        Rewrites entire connectivities

        Sign means the direction of the element
        """
        l = len(self.nodes)
        self.connectivities = [0] * (l * (l - 1) // 2)
        elemids = [0] * (l * (l - 1) // 2)
        for el_id in range(len(self.elems)):
            elem = self.elems[el_id]
            node1 = elem.nodes[0]
            node2 = elem.nodes[1]
            con1, _ = self.binary_search_node(0, len(self.nodes) - 1, node1)
            con2, _ = self.binary_search_node(0, len(self.nodes) - 1, node2)
            n = max(con1, con2)
            m = min(con1, con2)
            if n == con1:
                sign = 1
            else:
                sign = -1
            self.connectivities[n * (n - 1) // 2 + m] = sign * self.elem_num[type(elem)]
            elemids[n * (n - 1) // 2 + m] = sign * (el_id + 1)
        self.conn_mat, conn_comp = self.connect2mat(self.connectivities)
        self.elids_mat, _ = self.connect2mat(elemids)
        return conn_comp

    def connect2mat(self, connectivities) -> tuple[np.ndarray, int]:
        """
        Returns the full connectivity matrix
        from the compact version : connectivities.
        """
        n = len(connectivities)
        l = (1 + math.isqrt(1 + 8 * n)) // 2
        mat = np.zeros((l, l), dtype=int)
        for i in range(l):
            for j in range(l):
                if i == j:
                    continue
                n = max(i, j)
                m = min(i, j)
                if n == i:
                    sign = 1
                else:
                    sign = -1
                mat[i, j] = sign * connectivities[n * (n - 1) // 2 + m]
        newarr = csr_matrix(mat)
        conn_comp = connected_components(newarr)[0]
        return mat, conn_comp

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

    def build_graph_conn_mat(self):
        """
        From the connectivity matrix built with the drawing,
        simplify it (remove wires) to obtain a simpler graph
        from which we will get our system A.x=b
        """
        self.graph_conn_mat = self.conn_mat.astype(str)
        self.graph_elids_mat = self.elids_mat.astype(str)
        gcm = self.graph_conn_mat
        gem = self.graph_elids_mat
        filtr = gcm == "0"
        gcm[filtr] = ""
        gem[filtr] = ""
        n = len(self.conn_mat)
        i = 0
        while i < n:
            j = i + 1
            while j < n:
                while j < n and i < n and "1" in gcm[i, j]:
                    gcm[i, j] = ""
                    gcm[j, i] = ""
                    gcm[i, :] = np.char.add(gcm[i, :], ",")
                    gcm[i, :] = np.char.add(gcm[i, :], gcm[j, :])
                    gcm[:, i] = np.char.add(gcm[:, i], ",")
                    gcm[:, i] = np.char.add(gcm[:, i], gcm[:, j])
                    gcm = np.delete(gcm, j, axis=0)
                    gcm = np.delete(gcm, j, axis=1)
                    gem[i, j] = ""
                    gem[j, i] = ""
                    gem[i, :] = np.char.add(gem[i, :], ",")
                    gem[i, :] = np.char.add(gem[i, :], gem[j, :])
                    gem[:, i] = np.char.add(gem[:, i], ",")
                    gem[:, i] = np.char.add(gem[:, i], gem[:, j])
                    gem = np.delete(gem, j, axis=0)
                    gem = np.delete(gem, j, axis=1)
                    n -= 1
                    j = i + 1
                j += 1
            i += 1
        np.fill_diagonal(gcm, "")
        np.fill_diagonal(gem, "")
        self.graph_conn_mat = gcm
        self.graph_elids_mat = gem
        return

    def build_graph_nodes_edges(self):
        """
        From the connectivity matrix with element indices
        on each edge, build the nodes and edges of the graph

        Phantom nodes that are on the extremity of a source
        (pressure/flow source, ground) get the special type
        "Source"
        """
        gem = self.graph_elids_mat
        self.graph_nodes = []
        self.graph_edges = []
        n = len(gem)
        for i in range(n):
            self.graph_nodes.append(GraphNode())
        for i in range(n):
            for j in range(i + 1, n):
                elids = gem[i, j].split(",")
                elids = list(filter(None, elids))
                for elid in elids:
                    elid = int(elid)
                    if elid > 0:
                        edge = GraphEdge(i, j, self.elems[elid - 1])
                        if isinstance(self.elems[elid - 1], Ground):
                            self.graph_nodes[j].set_type("Source")
                    else:
                        edge = GraphEdge(j, i, self.elems[-elid - 1])
                        if isinstance(self.elems[-elid - 1], Ground):
                            self.graph_nodes[i].set_type("Source")
                    self.graph_edges.append(edge)
                    self.graph_nodes[i].add_edge(edge)
                    self.graph_nodes[j].add_edge(edge)
        return
    
    def graph_max_len_non_branching_paths(self) -> tuple[list, list]:
        """
        See max_len_non_branching_paths

        Adapted here for graph nodes and edges
        """
        Paths = []
        StartEnds = []
        for i in range(len(self.graph_nodes)):
            graphnode = self.graph_nodes[i]
            if len(graphnode.edges) != 2:
                for edge in graphnode.edges:
                    startend = []
                    startend.append(i)
                    non_branching_path = []
                    non_branching_path.append(edge)
                    if edge.start != i:
                        i1 = edge.start
                    else:
                        i1 = edge.end
                    graphnode1 = self.graph_nodes[i1]
                    prevedge = edge
                    k = 0
                    while len(graphnode1.edges) == 2:
                        for e in graphnode1.edges:
                            if prevedge is not e:
                                non_branching_path.append(e)
                                break
                        prevedge = non_branching_path[-1]
                        if prevedge.start != i1:
                            i1 = prevedge.start
                        else:
                            i1 = prevedge.end
                        graphnode1 = self.graph_nodes[i1]
                        k += 1
                        if k == 10000:
                            print("Error in branching path ", graphnode1)
                            return
                    startend.append(i1)
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
