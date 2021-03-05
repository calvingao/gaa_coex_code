# This is the Free Space Propagation Model
import constant
import geopy.distance
import numpy as np

I_max = constant.I_max      # Upper bound for calculating Point Interference Coordination
I_min = constant.I_min      # Lower bound for calculating Point Interference Coordination
rx_power_min = constant.rx_power_min    # minimum rx power for calculating IM in area interference coordination
tx_frequency = constant.lb_channels_frequency   # signal frequency for calculating propagation


def get_ew(cbsdpair, ic):
    """
    This Method returns edge weight of the given pair of CBSDs,
    using Free Space Propagation and selected Interference Coordination.

    Input:
            cbsdpair:  the pair of cbsd objects
                :type cbsdpair:    Tuple[CBSD, CBSD]

            ic:     interference coordination  "area", "point"
                :type ic:    str
    Returns:
            ew as edge weight, float [0, 1]
    """

    cbsd1 = cbsdpair[0]
    cbsd2 = cbsdpair[1]

    # Calculate Interference Metric for each CBSD based on Interference Coordination
    IM_1 = get_im_area(cbsd1, cbsd2) if ic == "area" else get_im_point(cbsd1, cbsd2)      # use global ic
    IM_2 = get_im_area(cbsd2, cbsd1) if ic == "area" else get_im_point(cbsd2, cbsd1)      # use global ic

    # Return max of IM1 and IM2 as edge weight
    return max(IM_1, IM_2)


# Calculate IM using Area Coordination: (CBSD1 interfered by CBSD2)
def get_im_area(cbsd1, cbsd2):
    # Distance between the cbsd pair
    distance = get_distance(cbsd1, cbsd2)

    # Radius of Both CBSDs' coverage
    r1 = get_distance_km_mhz(tx_frequency, cbsd1.TxPower, rx=rx_power_min)
    r2 = get_distance_km_mhz(tx_frequency, cbsd2.TxPower, rx=rx_power_min)

    area1 = np.pi * r1 * r1
    overlap = get_overlap(r1, r2, distance)     # call function to get overlap area

    return overlap/area1    # by definition, return fraction of overlap


# Calculate IM using Point Coordination: (CBSD1 interfered by CBSD2)
def get_im_point(cbsd1, cbsd2):
    # Distance between the cbsd pair
    distance = get_distance(cbsd1, cbsd2)
    I = get_rx_km_mhz(tx_frequency, cbsd2.TxPower, distance)
    # Use Global I_min, I_max
    if I < I_min:
        return 0
    elif I > I_max:
        return 1.0
    else:
        return float(I-I_min)/(I_max - I_min)


# Calculate distance between two CBSDs in km
def get_distance(cbsd1, cbsd2):
    coodinate1 = (cbsd1.latitude, cbsd1.longitude)
    coodinate2 = (cbsd2.latitude, cbsd2.longitude)
    return geopy.distance.vincenty(coodinate1, coodinate2).km


# Calculate transmit distance with given propagation loss
def get_distance_km_mhz(freq, tx, rx):
    pl = tx - rx
    d = (10**((pl-32.44)/20))/freq
    return d


# Calculate Rx power with given distance of propagation
def get_rx_km_mhz(freq, tx, distance):
    pl = np.log10(distance * freq) * 20 + 32.44
    rx = tx - pl
    return rx

# methods to return overlap area of two intersecting circles
def get_overlap(R, r, d):
    """
    Calculate overlap area of two intersecting circles
    Used for calculating free space area interference coordination

    :param R: Radius of the First Circle
    :param r: Radius of the Second Circle
    :param d: Distance between two Centroids
    :return: Overlap Area
    """
    if d <= abs(R-r):
        # One circle is entirely enclosed in the other.
        return np.pi * min(R, r)**2
    if d >= r + R:
        # The circles don't overlap at all.
        return 0

    r2, R2, d2 = float(r)**2, float(R)**2, float(d)**2
    alpha = np.arccos((d2 + r2 - R2) / (2*d*r))
    beta = np.arccos((d2 + R2 - r2) / (2.0*d*R))
    result = r2 * alpha + R2 * beta - R * np.sin(beta) * d
    return result
