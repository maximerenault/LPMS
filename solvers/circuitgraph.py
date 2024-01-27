from elements.node import Node
import numpy as np
from scipy.sparse.csgraph import connected_components
from scipy.sparse import csr_matrix

class CircuitGraph() :
    def __init__(self) -> None:
        self.elems = []
        self.nodes = []
        self.connectivities = []

    def add_elem(self, elem) -> None:
        self.elems.append(elem)

    def add_elem_nodes(self, elem) -> None:
        '''
        Uses a binary search to insert new nodes
        in nodes list, or to find existing nodes.
        '''
        for i in range(2):
            index, exists = self.binary_search_node(0,len(self.nodes)-1,elem.nodes[i])
            if exists :
                for el in elem.nodes[i].elems :
                    self.nodes[index].elems.append(el)
                elem.nodes[i] = self.nodes[index]
            else :
                self.nodes.insert(index, elem.nodes[i])

    def gen_connx(self) -> None:
        '''
        Generates compact connectivity list
        based on elements and nodes.
        Rewrites entire connectivities.
        '''
        n = len(self.nodes)
        self.connectivities = [0]*(n*(n-1)//2)
        for el_id in range(len(self.elems)) :
            elem = self.elems[el_id]
            node1 = elem.nodes[0]
            node2 = elem.nodes[1]
            con1, _ = self.binary_search_node(0,len(self.nodes)-1,node1)
            con2, _ = self.binary_search_node(0,len(self.nodes)-1,node2)
            n = max(con1,con2)
            m = min(con1,con2)
            self.connectivities[n*(n-1)//2+m] = el_id+1
        print(self.connect2mat())

    def gen_connectivities(self) -> None:
        '''
        DEPRECATED
        Generates compact connectivities list
        based on elements coordinates.
        Rewrites entire nodes and connectivities.
        '''
        self.nodes = []
        self.connectivities = []
        for el_id in range(len(self.elems)) :
            elem = self.elems[el_id]
            coords = elem.getcoords()
            con1 = -1
            con2 = -1
            for i in range(len(self.nodes)) :
                node = self.nodes[i]
                if (coords[:2]==node.coords).all():
                    con1 = i
                if (coords[2:]==node.coords).all():
                    con2 = i
            
            nb_new = 0
            if con1 == -1 :
                self.nodes.append(Node(coords[0],coords[1]))
                con1 = len(self.nodes)-1
                nb_new+=1
            if con2 == -1 :
                self.nodes.append(Node(coords[2],coords[3]))
                con2 = len(self.nodes)-1
                nb_new+=1

            n = max(con1,con2)
            m = min(con1,con2)
            if nb_new == 0 :
                self.connectivities[n*(n-1)//2+m] = el_id+1
            if nb_new == 1 :
                for i in range(len(self.nodes)-1):
                    self.connectivities.append(0)
                self.connectivities[n*(n-1)//2+m] = el_id+1
            if nb_new == 2 :
                for i in range(2*len(self.nodes)-3):
                    self.connectivities.append(0)
                self.connectivities[n*(n-1)//2+m] = el_id+1
        # print(self.connect2mat())

    def connect2mat(self) -> np.ndarray:
        '''
        Returns the full connectivity matrix
        from the compact version : connectivities.
        '''
        l = len(self.nodes)
        mat = np.zeros((l,l),dtype=int)
        for i in range(l):
            for j in range(l):
                if i==j :
                    continue
                n = max(i,j)
                m = min(i,j)
                mat[i,j] = self.connectivities[n*(n-1)//2+m]
        newarr = csr_matrix(mat)
        print('Nb of connected components :',connected_components(newarr)[0])
        return mat
    
    def show(self) -> None:
        return
    
    def binary_search_node(self, low, high, node) -> (int, bool):
        '''
        Returns the index of the node for insertion,
        or the index of the existing node if exists==True.
        '''
        index = 0
        exists = False
        snodes = self.nodes
        l = len(snodes)
        if l == 0 :
            index = 0
            exists = False
        elif high >= low:
            mid = (high+low)//2
            scoords = snodes[mid].getcoords()
            coords = node.getcoords()
            if (scoords==coords).all():
                index = mid
                exists = True
            elif scoords[0]>coords[0]:
                return self.binary_search_node(low,mid-1,node)
            elif scoords[0]==coords[0] and scoords[1]>coords[1]:
                return self.binary_search_node(low,mid-1,node)
            else :
                return self.binary_search_node(mid+1,high,node)
        else :
            index = low
            exists = False
        return index, exists
    
    def binary_search_elem(self, low, high, elem) -> (int, bool):
        '''
        Returns the index of the elem for insertion,
        or the index of the existing elem if exists==True.
        Normally elems are created in order so there shouldn't be any use for the firt option.
        '''
        index = 0
        exists = False
        selems = self.elems
        l = len(selems)
        if l == 0 :
            index = 0
            exists = False
        elif high >= low:
            mid = (high+low)//2
            sid = selems[mid].ids[0]
            id = elem.ids[0]
            if sid==id:
                index = mid
                exists = True
            elif sid>id:
                return self.binary_search_elem(low,mid-1,elem)
            else :
                return self.binary_search_elem(mid+1,high,elem)
        else :
            index = low
            exists = False
        return index, exists
    
    def del_elem(self,index) -> None:
        '''
        Deletes the element at position [index].
        Also deletes associated nodes if they are
        not used anymore.
        '''
        elem = self.elems[index]
        for i in range(2):
            index, exists = self.binary_search_node(0,len(self.nodes)-1,elem.nodes[i])
            if exists and elem in self.nodes[index].elems :
                self.nodes[index].elems.remove(elem)
                l = len(self.nodes[index].elems)
                if l==0 :
                    self.nodes.pop(index)
        self.elems.remove(elem)