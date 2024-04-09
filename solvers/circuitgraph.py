from elements.node import Node
from elements.wire import Wire
from elements.ground import Ground
from scipy.sparse.csgraph import connected_components
from scipy.sparse import csr_matrix
from solvers.graphedge import GraphEdge
from solvers.graphnode import GraphNode
from bisect import bisect_left, bisect_right


class CircuitGraph:
    def __init__(self, cnodes, celems) -> None:
        """
        A class that contains a directional graph representation of the circuit
        and allows for communication with the circuit solver.
        """
        self.nodes, self.edges = self.convert_circuit_to_graph(cnodes, celems)

    def convert_circuit_to_graph(self, cnodes: list[Node], celems: list[Wire]):
        cnodes = sorted(cnodes)
        nodes, edges = [], []
        edgedict = {celem: [-1, -1] for celem in celems if type(celem) != Wire}

        while len(cnodes) > 0:
            # extract first sublist of identical nodes
            idend = bisect_right(cnodes, cnodes[0])
            subcnodes = cnodes[0:idend]
            del cnodes[0:idend]

            nodes.append(GraphNode())
            idnode = len(nodes) - 1

            for cnode in subcnodes:
                celem = cnode.elems[0]
                if type(celem) == Wire:
                    # if we reach a wire, we collapse it
                    otherend = celem.get_other_end(cnode)
                    idstart = bisect_left(cnodes, otherend)
                    idend = bisect_right(cnodes, otherend)
                    # we prevent going back through the same wire by removing the node
                    # can't use list.remove because of the ordering of class Node
                    for i in range(idstart, idend):
                        if cnodes[i].elems[0] == celem:
                            del cnodes[i]
                            break
                    subcnodes += cnodes[idstart : idend - 1]
                    del cnodes[idstart : idend - 1]
                else:
                    # for other elements we save the position of the node
                    edgedict[celem][celem.get_node_id(cnode)] = idnode
                    if isinstance(celem, Ground) and celem.get_node_id(cnode) == 1:
                        nodes[-1].set_type("Source")

        for celem in celems:
            if type(celem) != Wire:
                start = edgedict[celem][0]
                end = edgedict[celem][1]
                edges.append(GraphEdge(start, end, celem))
                nodes[start].add_edge(edges[-1])
                nodes[end].add_edge(edges[-1])

        return nodes, edges

    def graph_max_len_non_branching_paths(self) -> tuple[list, list]:
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
        for i, node in enumerate(self.nodes):
            if len(node.edges) != 2:
                for edge in node.edges:
                    startend = []
                    startend.append(i)
                    non_branching_path = []
                    non_branching_path.append(edge)
                    if edge.start != i:
                        i1 = edge.start
                    else:
                        i1 = edge.end
                    node1 = self.nodes[i1]
                    prevedge = edge
                    k = 0
                    while len(node1.edges) == 2:
                        for e in node1.edges:
                            if prevedge is not e:
                                non_branching_path.append(e)
                                break
                        prevedge = non_branching_path[-1]
                        if prevedge.start != i1:
                            i1 = prevedge.start
                        else:
                            i1 = prevedge.end
                        node1 = self.nodes[i1]
                        k += 1
                        if k == 10000:
                            print("Error in branching path ", node1)
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