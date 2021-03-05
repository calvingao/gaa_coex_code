# This is the Hybrid Propagation Model
import constant
from reference_models.propagation import wf_hybrid

I_max = constant.I_max      # Upper bound for calculating Point Interference Coordination
I_min = constant.I_min      # Lower bound for calculating Point Interference Coordination
rx_power_min = constant.rx_power_min    # minimum rx power for calculating IM in area interference coordination

# Get Edge Weight of the given pair of CBSDs under determined Interference Coordination
def get_ew(cbsdpair, ic):
    """
    This Method returns edge weight of the given pair of CBSDs,
    using Hybrid Propagation and selected Interference Coordination.

    Input:
            cbsdpair:  the pair of cbsd objects
                :type cbsdpair:    Tuple[CBSD, CBSD]

            ic:     interference coordination  "area", "point"
                :type ic:    str

    Pre-Conditions:
            For area coordination, each CBSD should have its coverage map (Rx_signal at each grid) ready.

    Returns:
            ew as edge weight, float [0, 1]
    """
    # Load each CBSD from the pair
    cbsd1 = cbsdpair[0]
    cbsd2 = cbsdpair[1]

    # Calculate Interference Metric for each CBSD based on Interference Coordination

    if ic == "area":
        return get_im_area(cbsd1, cbsd2)

    else:
        IM_1 = get_im_point(cbsd1, cbsd2)
        IM_2 = get_im_point(cbsd2, cbsd1)

        # Return max of IM1 and IM2 as edge weight
        return max(IM_1, IM_2)


# Calculate Interference Metric using Area Coordination
def get_im_point(cbsd1, cbsd2):
    """
    Call Hybrid propagation model to calculate Interference Metric of CBSD1 that is interferred by CBSD2
    Using Point Coordination

    Input:
            cbsd1:  CBSD object that is interferred.
                :type cbsd1:    CBSD

            cbsd2:  CBSD object that is interferring (as noise).
                :type cbsd2:    CBSD

    Returns:
            Interference Metrics as float
    """
    # Call Hybrid Propagation Model to calculate signal loss from cbsd2 at the location of cbsd1
    loss = wf_hybrid.CalcHybridPropagationLoss(cbsd2.latitude, cbsd2.longitude, cbsd2.height,
                                               cbsd1.latitude, cbsd1.longitude, cbsd1.height,
                                               cbsd_indoor=cbsd2.indoor, region=cbsd2.region_type,
                                               reliability=0.5)

    # Calculate Signal Strength by substracting loss from the transmitter power
    Ix = cbsd2.TxPower - loss[0]

    # Use Global I_min, I_max  to calculate the Interference Metric
    if Ix < I_min:
        return 0
    elif Ix > I_max:
        return 1.0
    else:
        return float(Ix - I_min)/(I_max - I_min)


# Calculate Interference Metric using Area Coordination
def get_im_area(cbsd1, cbsd2):
    """
    Calculate Interference Metric of CBSD1 that is interferred by CBSD2
    Using Area Coordination (Fraction of overlapped coverage in CBSD1's coverage)

    Input:
            cbsd1:  CBSD object that is interferred.
                :type cbsd1:    CBSD

            cbsd2:  CBSD object that is interferring (as noise).
                :type cbsd2:    CBSD

    Returns:
            Interference Metrics as float
    """
    # Filter the grid that has signal strength no less than the minimum value (-96 by default)
    effective_coverage_1 = {grid for grid in cbsd1.coverage.keys() if cbsd1.coverage.get(grid) >= rx_power_min}
    effective_coverage_2 = {grid for grid in cbsd2.coverage.keys() if cbsd2.coverage.get(grid) >= rx_power_min}

    # Find the overlap grids
    overlap = effective_coverage_1.intersection(effective_coverage_2)

    # calculate the areas by counting the number of grids
    area_1 = len(effective_coverage_1)
    area_2 = len(effective_coverage_2)
    area_overlap = len(overlap)

    # By definition, return IM as the fraction of overlapped area in the coverage.
    # This prevents division by 0. area_1 = 0 exists when grid size is too high.
    if area_overlap == 0:
        return 0
    else:
        return (area_overlap * 1.0)/min(area_1, area_2)


# Get the Rx Signal Strength from a cbsd to the location
def get_rx_signal_point((cbsd, location)):
    """
    This Method returns the Rx Signal Strength of a CBSD to a location using Hybrid Model

    Input:
            cbsd:  a cbsd object
                :type cbsd CBSD

            location, the coordinate of the location
                :type location Tuple[float, float]
    Returns:
            Rx_Signal:  The signal strength, float
    """
    lat_rx = location[0]    # latitude of the location
    lon_rx = location[1]    # longitude of the location
    height_rx = 0           # Default AGL of the Rx location is set to 0

    # call the method in wf_hybrid (hybrid model) to calculate the propagation loss from the CBSD to the location
    loss = wf_hybrid.CalcHybridPropagationLoss(cbsd.latitude, cbsd.longitude, cbsd.height,
                                               lat_rx, lon_rx, height_rx,
                                               cbsd_indoor=cbsd.indoor, region=cbsd.region_type,
                                               reliability=0.5)

    # Convert to Rx Signal
    Rx_Signal = cbsd.TxPower - loss[0]

    return Rx_Signal
