import gaa_graph_coloring as gc
import numpy as np
from typing import Dict, Set, FrozenSet


# Coexistence Group
class CxG:
    # Constructor
    def __init__(self, uid):
        """
        This is the Coexistence Group
        """
        self.id = uid
        # CBSDs
        self.CBSDs = set()  # type: Set[str]

        # Edges
        self.edges = set()  # type: Set[FrozenSet[str, str]]

        # Chromatic Number
        self.chromatic = 0  # type: int

    # CxG Grouping related Methods
    def add_cbsd(self, cbsd_id):
        """
        Add ids of target CBSD to this CxG
        This function is vectorized for efficiency.

        Inputs:
            cbsd_id (scalar or a set):
                id(s) of target CBSD(s) to assign to this CxG

        Post-Condition:
            self.CBSDs updated with new added CBSDs
        """
        if np.isscalar(cbsd_id):
            self.CBSDs.add(cbsd_id)
        else:
            self.CBSDs.update(cbsd_id)

    def set_edges(self, ewt, th):
        """
        Set edges from the edge weight table and threshold

        Inputs:
            ewt:
                Edge Weight Table of a given set of CBSDs
                :type ewt: Dict[FrozenSet[int: int] : float]

            th:
                Edge Threshold
                :type th: float

        Post-Condition:
            A subset of Edge weight table is selected from the given set,
            and contains only pairs of CBSDs in this CxGs
            self.ew_table is set to the above subset.
        """
        self.edges = {key for key, val in ewt.items()
                      if key.issubset(self.CBSDs) and val > th
                      }

    def coloring(self):
        """
        Set edges based on the edge weight table of the CXG and the given threshold.
        Then perform graph coloring for all included CBSDs
        Use Welsh-Powell algorithm

        Pre-Condition:
            CBSDs are added, edges is set

        Post-Condition:
            Get color assignment based on current CBSDs and edges

        Returns:
            Color Assignment in form of Dictionary, node as key and color as val.
                chromatic_number, color_assignment   (int, Dict[str: int])
        """

        # Call graph coloring tools with all CBSDs and edges
        result = gc.coloring(self.CBSDs, self.edges)
        self.chromatic = len({val for val in result.values()})
        return self.chromatic, result
