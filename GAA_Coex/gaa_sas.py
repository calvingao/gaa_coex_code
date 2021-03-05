from typing import Dict, List, Tuple, Set, FrozenSet
from gaa_cbsd import CBSD
from gaa_cxg import CxG
import gaa_propagation as pm
import os
import json
import numpy as np
import geopy
import geopy.distance as gd
import ndpool as mp


# Find all unconnected sub-graphs from given graph
def get_sub_graph_BFS(neighbors, edges):
    """
    Method to find all sub-graphs in a graph, where all vertex in each sub-graph are directly or indirectly connected
    Algorithm BFS

    Input:
        neighbors:
            all vertex of the graph and the list of its neighbors
            :type neighbors: Dict[str: set[str]]

        edges:   all edges
            :type edges: Set[FrozenSet[str, str]]

    Output:
        List of sets of vertex of each sub-graph
            :return: List[Set[str]]
    """
    # Find all sub_graphs as the connected sets (applying BFS)
    sub_graphs = []
    while len(edges) != 0:
        sub_graph = set(edges.pop())    # Pop an edge from the edges, add both CBSDs in the pair to a new sub-graph
        new_added = set(sub_graph)      # mark all the new added CBSDs as new added (for future find their neighbors)

        while len(new_added) != 0:      # Repeat until every added CBSD has been searched for neighbors
            new_edges = set()           # Create an empty set for new edges
            for x in new_added:                         # Search and add every neighbor of the new added CBSDs
                for y in neighbors[x]:
                    new_edges.add(frozenset((x, y)))    # Record the new added edges
            edges.difference_update(new_edges)          # Update the edges to remove the ones added to the sub-graph
            new_nodes = set()
            for z in new_edges:                         # Find out the new CBSDs from the new added edges
                new_nodes.update(z)
            new_added = new_nodes.difference(sub_graph)     # Refresh the new_added CBSDs for next search
            sub_graph.update(new_nodes)                     # Update the member of the sub-graph
        sub_graphs.append(sub_graph)    # When finishes, append the current sub-graph to the list

    # Append all stand alone CBSDs, each as a singleton CS
    sub_graphs.extend([{x} for x in neighbors.keys() if len(neighbors[x]) == 0])

    return sub_graphs


# Graph-Coloring a CxG with given threshold of edge-weight
def color_cxg(cxg):
    """
    Call Method of the CxG class to get graph-coloring result
    For Multi-Processing use

    Inputs:
        cxg:
            Coexistence Group

    Returns:
        Color Assignment in form of Dictionary, node as key and color as val.
            chromatic_number, color_assignment   (int, Dict[str: int])
    """
    return cxg.coloring()


class SAS:
    """
    The SAS that manages CBSDs and Spectrum Channels
    """
    def __init__(self, propagation="itm", coordination="area", num_chs=8):

        # Configuration Parameters:
        self.propagation = propagation      # type: str     # Propagation Model, "itm"; "freespace", "Hybrid"
        self.coordination = coordination    # type: str     # Coordination, default: "area"; "point"

        # CBSDs
        self.CBSDs = set()      # type: Set[CBSD]           # Set of All managed CBSDs

        self.grids = {}         # type: Dict[int: Tuple[float, float]]      # Target Area, used in area coordination
        self.ew_table = {}      # type: Dict[FrozenSet[str, str]: float]  # Table of all Edge Weights

        # Groups
        self.CSs = []           # type: List[dict]           # List of Connected Sets

        # GAA Resource  //Use integer for current ver. wgao 03-20-2019
        self.channels = set(range(1, 1 + num_chs))          # type: Set[int]            # Available Channels

        # # Temporary List    //Use for adding individual CBSDs, To be implemented
        # self.temp_list = []     # type: List[CBSD]          # CBSDs that are not or temporarily assigned

    # # Reset SAS members and assignments:
    # Reset all
    def reset_all(self):    # chs for available channels
        self.CBSDs = set()
        self.reset_ew_table()
        self.clear_temp_list()

    # Reset Edge Weight Table
    def reset_ew_table(self):
        self.ew_table = {}
        self.reset_CS()     # Connected Sets assignment will be reset as well

    # Reset Connected Sets Assignment
    def reset_CS(self):
        self.CSs = []

    # Reset Available Channels
    def reset_channels(self, chs=None):
        if chs is None:
            self.channels = set(range(1, 9))    # Default use 8 channels from 1 to 8
        else:
            self.channels = chs

    # Reset Temporary List
    def clear_temp_list(self):
        self.temp_list = []

    # #
    # def add_channel(self, ch):
    #     self.channels.add(ch)
    #
    # def remove_channel(self, ch):
    #     self.channels.remove(ch)

    # SAS Operations:
    # Load CBSD from file in json format:
    def load_CBSDs_file(self, filename, grid_size=0.05, set_cxg=True):
        """
        Create CBSDs from given tuples of raw CBSD data
        Append to existing list of CBSDs

        Inputs:
            filename:   File with raw CBSD data in the format of json
                :type filename: str

            grid_size:  grid_size used to split target area to grids, valid in Area Coordination Only
                :type grid_size: float

            set_cxg:    choose whether to use pre-assigned CxG
                :type set_cxg: bool

        Post-Condition:
            CBSDs are created from given raw data, appended to self.CBSDs
            if area coordination, self.grids is set
        """
        # Load scenario configuration from file in json format
        f = open(filename)
        scenario = json.load(f)

        # Call method to load CBSDs using the dictionary converted from json
        self.load_CBSDs(scenario, grid_size=grid_size, set_cxg=set_cxg)

    # Load CBSD raw data from dictionary format
    def load_CBSDs(self, scenario, grid_size=0.05, set_cxg=True):
        """
        Create CBSDs from given tuples of raw CBSD data
        Append to existing list of CBSDs

        Inputs:
            scenario:   Dictionary with raw CBSD data in the format of json
                :type scenario: dict

            grid_size:  grid_size used to split target area to grids, valid in Area Coordination Only
                :type grid_size: float

            set_cxg:    choose whether to use pre-assigned CxG
                :type set_cxg: bool

        Post-Condition:
            CBSDs are created from given raw data, appended to self.CBSDs
            if area coordination, self.grids is set
        """
        # Fetch dict of cbsds
        cbsds = scenario.get("CBSDs")   # type: list

        # Add each CBSD to the SAS
        for cbsd_info in cbsds:
            # Create CBSD object using configuration
            cbsd_object = CBSD(cbsd_info.get("id"),
                               cbsd_info.get("latitude"),
                               cbsd_info.get("longitude"),
                               cbsd_info.get("agl"),
                               cbsd_info.get("eirp"),
                               cbsd_info.get("region_type"),
                               cbsd_info.get("indoor"),
                               cbsd_info.get("cat")
                               )
            # Initialize state with CxG assignment
            if set_cxg and cbsd_info.get("CxG") is not None:
                cbsd_object.set_state(cxg_id=cbsd_info.get("CxG"))
            else:
                cbsd_object.set_state()

            # Add to the set
            self.CBSDs.add(cbsd_object)

        # if SAS is set using area coordination, generate Grids with given area information
        if self.coordination == "area":
            area = scenario.get("area")
            self.set_grid(area.get("lat0"), area.get("lon0"), area.get("width"), area.get("length"), grid_size)

    # Create Grid for area coordination
    def set_grid(self, lat0, lon0, width, length, grid_size=0.05):
        """
        Set Target area based on given centroid coordinate and w, l of the rectangle area

        Input:
                lat0, lon0:         Centroid coordinate
                width, length:      Width, Length of the area
                grid_size:          width of each grid, in km

        Post-Condition:
                self.grids updated
        """
        # Generate grid coordinate in (x, y)
        xs = np.arange(float(-width + grid_size)/2, float(width + grid_size)/2, grid_size)
        ys = np.arange(float(-length + grid_size)/2, float(length + grid_size)/2, grid_size)

        # Convert to coordinate
        index = 1
        start = geopy.Point(lat0, lon0)
        for _x in xs:
            for _y in ys:
                # Get Coordinate of (_x, _y) with (lat0, lon0) at (0, 0)
                north = gd.VincentyDistance(kilometers=_y)
                east = gd.VincentyDistance(kilometers=_x)
                point = north.destination(east.destination(start, 90), 0)
                self.grids.update({index: (point[0], point[1])})
                # Update index
                index += 1

    # For Area Coordination, Create Coverage map for all CBSDs
    def create_coverage(self):

        # Create query for multi-processing call
        query = zip(self.CBSDs,                             # CBSD
                    [self.grids] * len(self.CBSDs),         # Grid
                    [self.propagation] * len(self.CBSDs)    # Propagation Model to use
                    )

        # Call functions to get all CBSDs' coverage
        pool = mp.Pool()
        signal_maps = pool.map(pm.get_coverage, query)
        pool.terminate()

        # set CBSDs' coverage with above result
        for cbsd, signal_map in zip(self.CBSDs, signal_maps):
            cbsd.set_coverage(signal_map)

        print "Coverage Maps Created"

    # Create Edge Weight Table for all managed CBSDs
    def create_ew_table(self):
        """
        Reset and Create Edge Weight Table from the beginning (for all CBSDs)
        Existing Edge Weight Table will be dropped

        Inputs:
            Min_Edge_threshold:     The threshold of edge weight where 2 CBSDs are considered to have potential interference
                :type Min_Edge_threshold: float, default 0

        Pre-Condition:
            CBSDs data have been loaded to SAS, Stored in self.CBSDs

        Post-condition:
            Edge Weight Table is created for each pair of CBSDs whose edge weight is above Minimum Edge threshold
        """
        # Reset Edge Weight Table
        self.reset_ew_table()

        # If Area Coordination, call method to create coverage for all CBSDs
        if self.coordination == "area":
            self.create_coverage()

        # Create all pairs of CBSDs in the list: C(n, 2)
        pairs = []  # type: List[Tuple[CBSD, CBSD]]
        all_cbsds = self.CBSDs.copy()
        while len(all_cbsds) >= 2:
            i = all_cbsds.pop()
            for j in all_cbsds:
                pairs.append((i, j))

        # Apply Propagation Model to get edge weight for each pair (with help of multiprocessing)
        p = mp.Pool()     # compute in parallel
        ret = p.map(pm.get_ew, zip(pairs,
                                   [self.propagation] * len(pairs),
                                   [self.coordination] * len(pairs)
                                   )
        )   # type: List[float]

        p.terminate()

        # Convert pairs to frozensets of CBSDs' id (hashable)
        keysets = []
        for pair in pairs:
            keysets.append(frozenset((pair[0].id, pair[1].id)))

        # Create Edge Weight Table for all edge weight pairs
        ewt = dict(zip(keysets, ret))
        print len([val for val in ewt.values() if val > 0])
        ewt = {key: val for key, val in ewt.items() if val > 0}     # Keep only ew > 0
        self.ew_table = ewt

    # Coloring the CBSDs interference graph
    def graph_coloring_all_until_satisfied(self, th_start=0.0, th_step=0.02):
        """
        Perform Graph Coloring to all CBSDs based on the Edge Weight Table, until the chromatic number
        of each connected set is no greater than the number of available channel.

        Input:
            th_start:       initial edge threshold used to create edges
                :type th_start: float

            th_step:        value to increase if the current edge threshold is not satisfied
                :type th_step: float

        Pre-Condition:
            Edge Weight Table is created and updated for current list of CBSDs

        Post-Condition:
            All CBSDs are graph colored and the result are stored in self.CSs include the members and threshold
        """
        all_cbsd_ids = {item.id for item in self.CBSDs}
        self.CSs = self.graph_coloring_until_satisfied(all_cbsd_ids, th_start=th_start, th_step=th_step)

    # Coloring a given CBSDs set with known ew table
    def graph_coloring_until_satisfied(self, cbsd_ids, th_start=0.0, th_step=0.02):
        """
        Perform Graph Coloring to the given set of CBSDs based on the Edge Weight Table, until the chromatic number
        of each connected set is no greater than the number of available channel.

        Input:
            cbsd_ids:       id of the CBSDs to be graph-colored
                :type cbsd_ids: Set[str]

            th_start:       initial edge threshold used to create edges
                :type th_start: float

            th_step:        value to increase if the current edge threshold is not satisfied
                :type th_step: float

        Pre-Condition:
            Edge Weight Table is created and updated for current list of CBSDs

        Returns:
            List of dict, each represents a Connected set with the member CBSDs, threshold, and Chromatic Number
                :type return: List[dict]

        """
        satisfied_CSs = []      # List to store CSs that has been graph colored and satisfies the requirement
        th_start = min(th_start, 1.0)   # threshold will not exceed 1.0

        # # Step 1: Based on the edge threshold, create Connected Sets of given CBSDs
        # Select the edges between involved CBSDs whose value >= edge threshold
        effective_edges = {k for k in self.ew_table.keys()
                           if k.issubset(cbsd_ids) and self.ew_table.get(k) > th_start
                           }

        # Initialize neighbor list for every involved CBSD
        neighbors = {}
        for cbsd in cbsd_ids:
            neighbors[cbsd] = set()

        # For the CBSD pair in every egde, add each other as the neighbor
        for key in effective_edges:
            tmp = list(key)
            neighbors[tmp[0]].add(tmp[1])
            neighbors[tmp[1]].add(tmp[0])

        # Find all sub_graphs where each represents a connected set (call the methods defined in this file)
        sub_graphs = get_sub_graph_BFS(neighbors, effective_edges)

        CSs = []
        for sub_graph in sub_graphs:
            members = dict.fromkeys(sub_graph, 0)
            one_CS = {"edge_threshold": th_start,       # Record the threshold used (no exceeds 1.0)
                      "members": members,               # Record members (CBSD ids), set color 0
                      "chromatic": 0                    # Initialize chromatic to 0
                      }
            CSs.append(one_CS)

        # # Step 2. Graph Coloring each Connected Set.
        # # Keep the satisfied ones, and repeat the rest with increased threshold
        for each_CS in CSs:
            each_CS = self.coloring_cs(each_CS)

            # if not satisfied, call the graph coloring method recursively with increased threshold
            if each_CS.get("chromatic") > len(self.channels) and each_CS.get("edge_threshold") < 1.0:
                # Find minimum edge weight value that is larger than the current threshold
                next_ew = min(val for k, val in self.ew_table.items()
                              if k.issubset(each_CS.get("members").keys()) and val > th_start)

                # keep increase next threshold until it exceeds the next minimum edge weight (to save time)
                next_th = th_start
                while next_ew > next_th:
                    next_th += th_step
                result = self.graph_coloring_until_satisfied(set(each_CS.get("members").keys()),
                                                             th_start=next_th,
                                                             th_step=th_step
                                                             )
                satisfied_CSs.extend(result)

            # Append satisfied CS to the list
            else:
                satisfied_CSs.append(each_CS)

        # # Step 3. Return list of satisfied CS
        return satisfied_CSs

    # Coloring the CBSDs interference graph
    def graph_coloring_all_at(self, th=0.0):
        """
        Perform Graph Coloring to all CBSDs based on the Edge Weight Table at a fixed edge threshold.

        Input:
            th:     edge threshold used to create edges
                :type th: float

        Pre-Condition:
            Edge Weight Table is created and updated for current list of CBSDs

        Post-Condition:
            All CBSDs are graph colored and the result are stored in self.CSs include the members and threshold
        """
        all_cbsd_ids = {item.id for item in self.CBSDs}
        self.CSs = self.graph_coloring_at(all_cbsd_ids, th=th)

    # Coloring a given CBSDs set with known ew table at a fixed threshold
    def graph_coloring_at(self, cbsd_ids, th=0.0):
        """
        Perform Graph Coloring to the given set of CBSDs based on the Edge Weight Table, until the chromatic number
        of each connected set is no greater than the number of available channel.

        Input:
            cbsd_ids:   id of the CBSDs to be graph-colored
                :type cbsd_ids: Set[str]

            th:         initial edge threshold used to create edges
                :type th: float

        Pre-Condition:
            Edge Weight Table is created and updated for current list of CBSDs

        Returns:
            List of dict, each represents a Connected set with the member CBSDs, threshold, and Chromatic Number
                :type return: List[dict]

        """
        colored_CSs = []      # List to store CSs that has been graph colored

        # # Step 1: Based on the edge threshold, create Connected Sets of given CBSDs
        # Select the edges between involved CBSDs whose value >= edge threshold
        effective_edges = {k for k in self.ew_table.keys()
                           if k.issubset(cbsd_ids) and self.ew_table.get(k) > th
                           }

        # Initialize neighbor list for every involved CBSD
        neighbors = {}
        for cbsd in cbsd_ids:
            neighbors[cbsd] = set()

        # For the CBSD pair in every egde, add each other as the neighbor
        for key in effective_edges:
            tmp = list(key)
            neighbors[tmp[0]].add(tmp[1])
            neighbors[tmp[1]].add(tmp[0])

        # Find all sub_graphs where each represents a connected set (call the methods defined in this file)
        sub_graphs = get_sub_graph_BFS(neighbors, effective_edges)

        CSs = []
        for sub_graph in sub_graphs:
            members = dict.fromkeys(sub_graph, 0)
            one_CS = {"edge_threshold": th,       # Record the threshold used
                      "members": members,         # Record members (CBSD ids), set color 0
                      "chromatic": 0              # Initialize chromatic to 0
                      }
            CSs.append(one_CS)

        # # Step 2. Graph Coloring each Connected Set.
        for each_CS in CSs:
            each_CS = self.coloring_cs(each_CS)
            colored_CSs.append(each_CS)

        # # Step 3. Return list of satisfied CS
        return colored_CSs

    # Graph Coloring selected Connected Set(s)
    def coloring_cs(self, target_cs):
        """
        Perform Graph Coloring to connected set(s) with given threshold (initial and incremental) until satisfied

        Input:
            target_cs:  Target Connected Set include members list and threshold used
                :type target_cs: dict

        Returns:
            colored connected sets
        """
        # Find member CBSDs in the target connected set
        members = target_cs.get("members")      # type: dict

        # Distinguish by CxG assignment, Create CxG objects
        CxG_ids = {cbsd.CxG for cbsd in self.CBSDs if cbsd.id in members.keys()}
        cxgs = []
        for cxg_id in CxG_ids:
            one_cxg = CxG(cxg_id)       # Create CxG object
            # Find all CBSDs in the Connected Set with current CxG number
            cbsds_of_cxg = [cbsd.id for cbsd in self.CBSDs if cbsd.id in members.keys() and cbsd.CxG == cxg_id]
            one_cxg.add_cbsd(cbsds_of_cxg)
            one_cxg.set_edges(self.ew_table, target_cs.get("edge_threshold"))
            cxgs.append(one_cxg)

        # Graph Color each CxG in parallel:
        p = mp.Pool()
        ret = p.map(color_cxg, cxgs)    # type: List[int, Dict[str: int]]
        p.terminate()

        # Fetch chromatic numbers and color_assignments from the result
        chromatic_numbers, color_assignments = zip(*ret)

        # Update Chromatic Number of Connected Set
        target_cs["chromatic"] = sum(chromatic_numbers)

        # Adjust Numbers to leave 0 for non-assigned, and range of color differs between CxGs
        c_start = 1
        all_color_assignment = {}
        for item in color_assignments:  #
            # Color start from next available color
            clrs = {key: val + c_start for key, val in item.items()}
            c_start = max(clrs.values()) + 1
            all_color_assignment.update(clrs)

        # Update Color Assignment for all members in target connected set
        target_cs["members"] = {key: all_color_assignment.get(key) for key in members.keys()}

        # Return CS
        return target_cs

    # Assign Channels to CBSDs
    def assign_channels(self, partial_assign=False):
        """
        Assign available channels to CBSDs based on graph coloring results

        Input:
            partial_assign:
                parameter used for assigning channels to CS with chromatic number > number of channels
                    (when fixed threshold is used)
                    if True, only the CBSDs whose color number <= total channels will be assigned with one channel
                    if False, no CBSDs will be assigned with channels
                :type partial_assign: bool

        Pre-Condition:
            self.CSs is not empty (graph-coloring has been performed)

        Post-Condition:
            CBSDs in self.CBSDs will be assigned with channels (in form of int representing channel id)

        """
        available_channels = list(self.channels)
        for cs in self.CSs:
            cn = cs.get("chromatic")        # Chromatic Number
            members = cs.get("members")     # type: dict    # Color Assignment
            chs_per_color = int(len(available_channels) / cn)        # number of channels per color

            member_objs = [x for x in self.CBSDs if x.id in members.keys()]
            for cbsd_obj in member_objs:
                color = members.get(cbsd_obj.id)

                # if chromatic number exceeds available channels, and partially assignment is used
                if partial_assign and cn > len(available_channels):
                    # Assign only CBSDs whose color number within available channels
                    if color <= len(available_channels):
                        channels = {available_channels[color-1]}
                    # CBSD whose color number larger than available channels will not be assigned
                    else:
                        channels = set()
                # if partial assignment is not applied (False), channels will be assigned using chs_per_color
                else:
                    # the n-th continuous channels (with the number of chs_per_color) will be assigned, n = color
                    channels = set(available_channels[(color-1) * chs_per_color: color * chs_per_color])

                # Set color and channels for the CBSD object
                cbsd_obj.set_color(color)
                cbsd_obj.set_channels(channels)

    # Get CatA/CatB configuration
    def get_cbsd_categories(self):
        """
        Returns the number of catA and catB CBSDs
        :return: (number of CatA, number of CatB)
        """
        num_cata = len({cbsd for cbsd in self.CBSDs if cbsd.antenna_cat == "cata"})
        num_catb = len(self.CBSDs) - num_cata
        return num_cata, num_catb

    # Get output ready content of CBSDs
    def get_cbsd_content(self):
        """
        Iterate the CBSD List and get content for output
        :return: List[dict]
        """
        content = [cbsd.get_state_content() for cbsd in self.CBSDs]
        return content

    # Get output ready content of coverage maps
    def get_coverage_content(self):
        """
        Iterate the CBSD List and get content for output
        :return: Dict[str: dict]
        """
        content = {cbsd.id: cbsd.get_coverage_content() for cbsd in self.CBSDs}
        return content

    # Get output ready content of Edges
    def get_ew_table_content(self):
        """
        Iterate the edge weight table and get content for output
        :return: str
        """
        content = "# " + self.propagation + "\n"    # First line indicates the propagation model used
        for pair in self.ew_table.keys():
            line = ""
            for n in pair:
                line += str(n) + ", "
            line += str(self.ew_table[pair]) + "\n"
            content += line
        return content

    # Export CBSDs status to the File
    def export_states(self, output_file):
        """
        Export the current states to Files:
            States of all CBSDs, with Edge Weight Table and (if exists) Area, Coverage

        Input:
            output_file:    filename for output states
            :type output_file str

        Pre-Condition:
            The method can be called between each 2 of the following steps for resilience
                1. Loading CBSDs
                2. Creating Edge Weight Table

        Post-Condition:
            States are saved to the following file
                <filename>.cbsd     CBSD states
                <filename>.ewt      Edge Weight Table
                <filename>.cvg      CBSD Coverage Map (area coordination only)
                <filename>.area     Area info with grid coordinates
        """
        # CBSD states
        cbsd_content = self.get_cbsd_content()

        # Edge Weight Table
        ewt_content = self.get_ew_table_content()

        filename = output_file

        # Check if folder exists
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # use sequence number to avoid overriding existing files
        index = 0
        outfile1 = filename + ".cbsd"
        outfile2 = filename + ".ewt"
        outfile3 = filename + ".cvg"
        outfile4 = filename + ".area"
        while os.path.exists(outfile1)\
                 or os.path.exists(outfile2)\
                 or os.path.exists(outfile3)\
                 or os.path.exists(outfile4):
            index += 1
            outfile1 = filename + "-" + str(index) + ".cbsd"
            outfile2 = filename + "-" + str(index) + ".ewt"
            outfile3 = filename + "-" + str(index) + ".cvg"
            outfile4 = filename + "-" + str(index) + ".area"

        # Store CBSD data
        f = open(outfile1, "w")
        json.dump(cbsd_content, f)

        # Store edge weight table data
        f = open(outfile2, "w")
        f.write(ewt_content)

        if self.coordination == "area":
            # Store coverage data
            coverage_content = self.get_coverage_content()
            f = open(outfile3, "w")
            json.dump(coverage_content, f)

            # Store area data
            f = open(outfile4, "w")
            json.dump(self.grids, f)

    # Import CBSDs status from the file
    def import_states(self, input_file):
        """
        Import CBSD states from Files:
            States of all CBSDs with Edge Weight Table and (if exists) Area and Coverage

        Input:
            input_file:    filename for import states
            :type input_file str

        Pre-Condition:
            The method can be called between each 2 of the following steps for resilience
                1. Loading CBSDs
                2. Creating Edge Weight Table

        Post-Condition:
            States are recovered from the following file
                <filename>.cbsd     CBSD states
                <filename>.ewt      Edge Weight Table
                <filename>.cvg      CBSD Coverage Map (area coordination only)
                <filename>.area     Area info with grid coordinates
        """

        # remove extension:
        if "/" in input_file:
            prefix = "/".join(input_file.split("/")[:-1]) + "/"
            fname = input_file.split("/")[-1]
        else:
            prefix=""
            fname = input_file

        if "." in fname:
            fname = prefix + ".".join(fname.split(".")[:-1])
        else:
            fname = prefix + fname

        cbsd_file = fname + ".cbsd"
        ewt_file = fname + ".ewt"
        cvg_file = fname + ".cvg"
        area_file = fname + ".area"

        # try to import CBSD first
        if os.path.exists(cbsd_file):

            self.reset_all()

            f = open(cbsd_file)
            cbsd_content = json.load(f)
            for cbsd_item in cbsd_content:
                # Fetch info from each piece of cbsd infomation and added to self.CBSDs
                cbsd_obj = CBSD(cbsd_item.get("id"),
                                cbsd_item.get("latitude"),
                                cbsd_item.get("longitude"),
                                cbsd_item.get("agl"),
                                cbsd_item.get("eirp"),
                                cbsd_item.get("region_type"),
                                cbsd_item.get("indoor"),
                                cbsd_item.get("cat")
                                )
                cbsd_obj.set_state(tx_power=cbsd_item.get("tx_power"),
                                   cxg_id=cbsd_item.get("CxG")
                                   )
                self.CBSDs.add(cbsd_obj)

            # try to import Edge Weight Table
            if os.path.exists(ewt_file):
                # Read only first line of ewt file for propagation model
                f = open(ewt_file)
                self.propagation = f.readline()[2:].rstrip()
                f.close()

                # Read the rest of the ewt file for "pair: ew"
                p1s, p2s, ews = np.loadtxt(ewt_file, dtype="int, int, float", delimiter=', ', comments="#", unpack=True)
                self.ew_table = dict(zip([frozenset((str(i), str(j))) for i, j in zip(p1s, p2s)], ews))

            if os.path.exists(cvg_file):
                # Read the cvg file for (cbsd; coverage_map)
                f = open(cvg_file)
                coverage_content = json.load(f)
                for cbsd_obj in self.CBSDs:
                    cvg_map = coverage_content.get(cbsd_obj.id)         # Use CBSD id to find coverage map
                    cvg_map = {int(k): v for k, v in cvg_map.items()}   # Ensure use int keys (grid_id)
                    cbsd_obj.set_coverage(cvg_map)                      # recover coverage map

            # try to import grid information (id)
            if os.path.exists(area_file):
                with open(area_file) as f:
                    gr = json.load(f)
                self.grids = {int(k): v for k, v in gr.items()}         # Ensure use int keys (grid_id)

    # Import Graph Coloring Result from the file
    def import_cs(self, input_file):
        """
        Import Graph Coloring Result from File:
            All Connected Sets with edge threshold, member CBSDs with color assignment, and chromatic number

        Input:
            input_file:    filename for import states
            :type input_file str

        Pre-Condition:
            The method can be called between each 2 of the following steps for resilience
                1. Loading CBSDs
                2. Creating Edge Weight Table
                3. Finishing Graph Coloring

        Post-Condition:
            States are recovered from the following file
                <filename>.gc       Edge Weight Table and threshold of connected sets
        """

        # remove extension:
        if "/" in input_file:
            prefix = "/".join(input_file.split("/")[:-1]) + "/"
            fname = input_file.split("/")[-1]
        else:
            prefix=""
            fname = input_file

        if "." in fname:
            fname = prefix + ".".join(fname.split(".")[:-1])
        else:
            fname = prefix + fname

        cs_file = fname + ".gc"

        # try to import graph coloring result
        if os.path.exists(cs_file):
            f = open(cs_file)
            self.CSs = json.load(f)

    # Export Graph Coloring Result Only
    def export_cs(self, output_file):
        """
        Export the graph coloring result to file:
            All Connected Sets with edge threshold, member CBSDs with color assignment, and chromatic number

        Input:
            output_file:    filename for output states
            :type output_file str

        Pre-Condition:
            The method can be called between each 2 of the following steps for resilience
                1. Loading CBSDs
                2. Creating Edge Weight Table
                3. Finishing Graph Coloring


        Post-Condition:
            States are saved to the following file
                <filename>.gc       Edge Weight Table and threshold of connected sets
                States of all CBSDs, with Edge Weight Table and (if exists) Area, Coverage
        """

        filename = output_file

        # Check if folder exists
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # use sequence number to avoid overriding existing files
        index = 0
        outfile = filename + ".gc"
        while os.path.exists(outfile):
            index += 1
            outfile = filename + "-" + str(index) + ".gc"

        # Store graph coloring result
        if len(self.CSs) > 0:
            f = open(outfile, "w")
            json.dump(self.CSs, f)
        else:
            print "Graph coloring result not ready!"

    def get_approach_3(self, et=0):
        """
        Apply Algorithm from approach 3 to calculate maximum bandwidth allocation for each CBSD
        and the inter-CxG interference

        Input:
            et:    edge threshold
            :type et float

        Pre-Condition:
            The method can be called after creating the edge weight table

        Returns:
            Dictionary of with CBSD id as the key, the value will include the number of CxGs within the cluster
                and the accumulated edge weight from CBSDs in other CxGs
                :return: dict

        """

        # Find effective edges based on given edge threshold
        effective_edges = {k for k in self.ew_table.keys()
                           if self.ew_table.get(k) > et
                           }

        # Initialize neighbor list for every involved CBSD
        neighbors = {}
        for cbsd in self.CBSDs:
            neighbors[cbsd.id] = set()

        # For the CBSD pair in every edge, add each other as the neighbor
        for key in effective_edges:
            tmp = list(key)
            neighbors[tmp[0]].add(tmp[1])
            neighbors[tmp[1]].add(tmp[0])

        # Create empty dict to return
        ret = {}

        for each_cbsd in self.CBSDs:
            # find all distinct CxGs the selected cbsd and its neighbors belong to
            cluster_cxg = {nb_cbsd.CxG for nb_cbsd in self.CBSDs
                           if nb_cbsd.id in neighbors[each_cbsd.id]}
            cluster_cxg.add(each_cbsd.CxG)

            # find all inter-cxg pairs of the current cbsd
            inter_cxg_pairs = [frozenset((each_cbsd.id, x.id)) for x in self.CBSDs if x.CxG != each_cbsd.CxG]

            # Find all inter-cxg pairs whose ew <= threshold (ignored but existing interference)
            potential_ix_pairs = [k for k in set(inter_cxg_pairs).intersection(self.ew_table.keys())
                                  if self.ew_table.get(k) <= et
                                  ]

            # Find all other end of the above potential pairs
            potential_neighbors = {each_cbsd.id}
            for each_pair in potential_ix_pairs:
                potential_neighbors.update(each_pair)
            potential_neighbors.remove(each_cbsd.id)

            # update the dict to return
            ret[each_cbsd.id] = (len(cluster_cxg), potential_neighbors)

        return ret
