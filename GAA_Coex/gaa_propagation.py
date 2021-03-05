# Propagation Model for edge weight calculation
from typing import Tuple
import constant
from gaa_cbsd import CBSD
import multiprocessing as mp     # Revised multiprocessing pool, supports non-daemonic process
import geopy.distance
import propagation_model.free_space as fs
import propagation_model.itm as itm
import propagation_model.hybrid as hybrid

no_edge_distance = constant.no_edge_distance   # kilometer, edge is not considered for distance greater than this
I_max = constant.I_max      # Upper bound for calculating Point Interference Coordination
I_min = constant.I_min      # Lower bound for calculating Point Interference Coordination


# Function (for Multi-Processing) to check if distance in range
def is_in_range((coordinate_1, grid_index, coordinate_2)):
    dist_km = geopy.distance.vincenty(coordinate_1, coordinate_2).km
    if dist_km <= no_edge_distance:
        return grid_index


# Handler for Edge Weight
def get_ew((cbsdpair, pm, ic)):
    """
    This is the method to return edge weight of the given pair of CBSDs,
    using selected Propagation Model.

    Input:
            cbsdpair:   The pair of CBSDs to get edge weight
                :type cbsdpair: Tuple[CBSD, CBSD]

            pm:         Propagation Model ("freespace", "itm", "hybrid")
                :type pm:   str

            ic:         Interference Coordination ("area"; "point")
                :type ic:   str

    Returns:
            edge weight between the two CBSDs
    """
    # Calculate Distance between the cbsd pair
    coordinate1 = (cbsdpair[0].latitude, cbsdpair[0].longitude)
    coordinate2 = (cbsdpair[1].latitude, cbsdpair[1].longitude)
    distance = geopy.distance.vincenty(coordinate1, coordinate2).km

    # Check if belong to same CNG and NEG
    # True if both in same CNG
    CNG_same = cbsdpair[0].CNG is not None and cbsdpair[0].CNG is not None and cbsdpair[0].CNG is cbsdpair[0].CNG
    # True if both in same CNG
    NEG_same = cbsdpair[0].NEG is not None and cbsdpair[0].NEG is not None and cbsdpair[0].NEG is cbsdpair[0].NEG

    # edge weight is considered as 0, if in same CNG or NEG, or distance large enough (defined in constant)
    if CNG_same or NEG_same or distance >= no_edge_distance:
        print "None"
        return 0

    # if from different CNG and NEG, and distance less than pre-defined value
    # call Propagation Model to calculate distance
    else:
        # Free Space Propagation
        if pm == "freespace":
            return fs.get_ew(cbsdpair, ic)

        # ITM Model
        elif pm == "itm":
            return itm.get_ew(cbsdpair, ic)

        # Hybrid (ITM-eHata) Model
        elif pm == "hybrid":
            return hybrid.get_ew(cbsdpair, ic)

        # Default
        else:
            return 0


# Handler for Area Coverage
def get_coverage((cbsd, grids, pm)):
    """
    Get the Signal Coverage of the cbsd within the given area.

    Input:
            cbsd:  a cbsd object
                :type cbsd: CBSD

            grids: The target area with grid_index and the coordinate of each grid
                :type grids: Dict[int: Dict]    # {grid_index: {"coordinate": (lat, lon), ...}}

            pm: The propagation model used
                :type pm:   str
    Returns:
            Signal Map, the signal strength in each grid as dictionary {grid_index: signal_strength}
            :type signal_map: Dict[int: float]
    """
    if pm == "itm" or pm == "hybrid":     # Only ITM and Propagation Model

        # Skip Step 1 for small area
        # # Step 1: Limit the location points to the range of the no_edge_distance (40km default)
        # coordinate_cbsd = (cbsd.latitude, cbsd.longitude)   # coordinate of the CBSD
        #
        # # List all pairs of cbsd/location for multi-processing
        # pairs = [(coordinate_cbsd, g_index, grids.get(g_index)) for g_index in grids.keys()]
        #
        # # Find and List all grid (locations) in defined (40km) range
        # pool_range = mp.Pool()
        # grids_in_range = set(pool_range.map(is_in_range, pairs))
        # # the list of all grids that are in defined (40km default) range
        # grids_in_range.difference_update({None})     # get rid of None
        #
        # pool_range.terminate()  # Important! Release Pool Resource!

        # let grids_in_range be all
        grids_in_range = grids

        # Step 2. Based on the list of grid, calculate the Rx signals
        # List all pairs of given CBSD and in-range grid, for multiprocessing query
        query = [(cbsd, grids.get(g_index)) for g_index in grids_in_range]
        pool_signal = mp.Pool()
        signals = []

        # Based on Propagation Model, call the functions to get the coverage map for the given CBSD
        if pm == "itm":   # Use ITM Model
            signals = pool_signal.map(itm.get_rx_signal_point, query)

        elif pm == "hybrid":   # Use Hybrid Model
            signals = pool_signal.map(hybrid.get_rx_signal_point, query)

        # Create Dictionary of {Grid_index: Signal_strength}
        signal_map = {grid_i: signal for grid_i, signal in zip(grids_in_range, signals)}
        pool_signal.terminate()     # Important! Release Pool Resource!

        return signal_map
