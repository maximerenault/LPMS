import numpy as np
from elements.capacitor import Capacitor
from elements.ground import Ground
from elements.inductor import Inductor
from elements.psource import PSource
from elements.resistor import Resistor
from solvers.graphedge import GraphEdge
from solvers.graphnode import GraphNode
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import copy


class CircuitSolver:
    def __init__(self) -> None:
        self.M1 = None  # Matrix for order 1 derivatives
        self.M0 = None  # Matrix for order 0 derivatives
        self.Source = None  # Vector for source terms
        self.LHS = None
        self.RHS = None
        self.nbP = 0
        self.nbQ = 0
        self.dt = 0.01
        self.maxtime = 10.0
        self.solution = None
        # Backwards Differentiation Formula
        self.time_integrations = ["BDF", "BDF2"]
        self.time_integration = None
        self.update_source_dict = {}
        self.update_M0_dict = {}
        self.update_M1_dict = {}
        self.listened = {}

    def set_dt(self, dt: float) -> None:
        self.dt = dt

    def get_dt(self) -> float:
        return self.dt

    def set_maxtime(self, maxtime: float) -> None:
        self.maxtime = maxtime

    def get_maxtime(self) -> float:
        return self.maxtime

    def set_time_integration(self, ti: str) -> None:
        self.time_integration = ti

    def export_full_solution(self, fname: str) -> None:
        names = []
        for i in range(self.nbP):
            try:
                names.append(self.listened[i])
            except:
                names.append("P"+str(i))
        for i in range(self.nbQ):
            try:
                names.append(self.listened[self.nbP+i])
            except:
                names.append("Q"+str(self.nbP+i))
        np.savetxt(
            fname,
            self.solution,
            fmt="%.11g",
            delimiter=" ",
            newline="\n",
            header=" ".join(names),
            footer="",
            comments="# ",
            encoding=None,
        )

    def export_listened_solution(self, fname: str) -> None:
        np.savetxt(
            fname,
            self.solution[[i for i in self.listened.keys()]],
            fmt="%.11g",
            delimiter=" ",
            newline="\n",
            header=" ".join([self.listened[i] for i in self.listened.keys()]),
            footer="",
            comments="# ",
            encoding=None,
        )

    def solve(
        self, nbP: int, nbQ: int, nodes: list[GraphNode], paths: list[list[GraphEdge]], startends: list[list[int]]
    ) -> int:
        """
        Method that takes all the steps to solve the system:
        - check solution existence necessary condition
        - adapts input data
        - allocates arrays
        - builds zero and first order differential matrices
        - builds source vector and give update dictionary for transient sources
        - takes steady state solution as initial state
        - builds LHS
        - solves LHS.x = RHS at each timestep
        """
        cns = self.check_no_solution(nbP, nbQ, paths, startends)
        if cns:
            return cns
        nodes, paths, startends = self.delete_node_sources(
            copy.deepcopy(nodes), copy.deepcopy(paths), copy.deepcopy(startends)
        )

        time = 0.0
        step = 0
        nb_step = int(self.maxtime / self.dt)
        self.nbP = nbP
        self.nbQ = nbQ
        self.M1 = np.zeros((nbP + nbQ, nbP + nbQ), dtype=float)
        self.M0 = np.zeros((nbP + nbQ, nbP + nbQ), dtype=float)
        self.Source = np.zeros((nbP + nbQ), dtype=float)
        self.solution = np.zeros((nbP + nbQ, nb_step + 1))

        self.build_M0M1(nbP, paths, startends)
        self.update_source_dict = self.build_source(paths)
        self.update_source(time)

        # Initializing with steady-state solution
        try:
            self.solution[:, :] = np.linalg.solve(self.M0, self.Source).reshape(-1, 1)
        except:
            return 2
        self.build_LHS()

        while step < nb_step:
            time += self.dt
            self.update_source(time)
            self.build_RHS(step)
            self.solution[:, step + 1] = np.linalg.solve(self.LHS, self.RHS)
            step += 1

        plt.plot(np.linspace(0, self.maxtime, nb_step + 1), self.solution.T)
        plt.show()

        return 0

    def build_M0M1(self, nbP, paths, startends) -> None:
        """
        Build matrices for zero and first order derivatives
        of the unknown vector
        """
        M1 = self.M1
        M0 = self.M0
        line = 0
        idQ = nbP
        for i in range(len(paths)):
            path = paths[i]
            startend = startends[i]
            idP0 = startend[0]
            for edge in path:
                if idP0 == edge.start:
                    idP1 = edge.end
                else:
                    idP1 = edge.start
                if type(edge.elem) == Resistor:
                    M0[line, idP1] = 1
                    M0[line, idP0] = -1
                    M0[line, idQ] = -edge.elem.get_value()
                elif type(edge.elem) == Capacitor:
                    M0[line, idP1] = 1
                    M0[line, idP0] = -1
                    M1[line, idQ] = -edge.elem.get_value()
                elif type(edge.elem) == Inductor:
                    M1[line, idP1] = edge.elem.get_value()
                    M1[line, idP0] = -edge.elem.get_value()
                    M0[line, idQ] = -1
                elif type(edge.elem) == Ground or type(edge.elem) == PSource:
                    idP1 = edge.start
                    M0[line, idP1] = 1
                idP0 = idP1
                line += 1
            idQ += 1
        # Branching equations
        arr = np.array(startends).flat
        unique, counts = np.unique(arr, return_counts=True)
        for i in range(len(counts)):
            if counts[i] > 1 and unique[i] != -1:
                idnode = unique[i]
                idQ = nbP
                for startend in startends:
                    if startend[0] == idnode:
                        M0[line, idQ] = -1
                    elif startend[1] == idnode:
                        M0[line, idQ] = 1
                    idQ += 1
                line += 1
        return

    def build_source(self, paths) -> dict:
        """
        Build live sources dict from list of paths
        """
        update_source_dict = {}
        line = 0
        for i in range(len(paths)):
            path = paths[i]
            for edge in path:
                if type(edge.elem) == PSource:
                    update_source_dict[line] = edge.elem.get_source()
                line += 1
        return update_source_dict

    def update_source(self, time) -> None:
        """
        Update source vector according to the live sources
        in update_source_dict
        """
        for line in self.update_source_dict.keys():
            self.Source[line] = self.update_source_dict[line](time)

    def build_LHS(self) -> None:
        """
        Build left hand side of the equation
        """
        self.LHS = np.zeros_like(self.M0)
        if self.time_integration == "BDF":
            self.LHS = self.M0 + self.M1 / self.dt
        elif self.time_integration == "BDF2":
            self.LHS = self.M0 + 3 * self.M1 / (2 * self.dt)
        return

    def build_RHS(self, step: int) -> None:
        """
        Build right hand side of the equation
        """
        self.RHS = np.zeros_like(self.Source)
        if self.time_integration == "BDF":
            self.RHS = self.Source + np.matmul(self.M1, self.solution[:, step] / self.dt)
        elif self.time_integration == "BDF2":
            self.RHS = self.Source + np.matmul(
                self.M1, (4 * self.solution[:, step] - self.solution[:, step - 1]) / (2 * self.dt)
            )
        return

    def check_no_solution(self, nbP, nbQ, paths, startends) -> int:
        """
        Check if the problem has a solution
        0 : OK
        1 : under constrained
        2 : over constrained
        """
        c = 0
        # Count equations from elements
        for path in paths:
            for edge in path:
                c += 1
        # Count equations from branching
        arr = np.array(startends).flat
        unique, counts = np.unique(arr, return_counts=True)
        for count in counts:
            if count > 1:
                c += 1
        # Compare with number of unknowns
        if c > nbP + nbQ:
            return 2
        if c < nbP + nbQ:
            return 1
        return 0

    def delete_node_sources(self, nodes, paths, startends) -> tuple[list, list, list]:
        """
        Method to remove annoying "Source" nodes that were
        used previously to define correctly the graph

        Since they are no use to build the system (as they provide the
        same pressure as the node on the other side of the edge) we
        remove them and update edges accordingly
        """
        rem = []
        for i in range(len(nodes)):
            node = nodes[i]
            if node.type == "Source":
                rem.append(i)
        rem.reverse()
        for i in rem:
            del nodes[i]
            for path in paths:
                for edge in path:
                    if edge.start == i:
                        edge.start = -1
                    if edge.end == i:
                        edge.end = -1
                    if edge.start > i:
                        edge.start -= 1
                    if edge.end > i:
                        edge.end -= 1
            for startend in startends:
                if startend[0] == i:
                    startend[0] = -1
                if startend[1] == i:
                    startend[1] = -1
                if startend[0] > i:
                    startend[0] -= 1
                if startend[1] > i:
                    startend[1] -= 1
        return nodes, paths, startends
