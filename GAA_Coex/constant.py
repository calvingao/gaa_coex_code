# Defines Constants used in GAA-GAA Coexistence

# Propagation Selector

# Select Propagation Model:
# 1: Free Space
# 2: ITM
# 3: ITM e-Hata Hybrid
propagation_model = 3

# Select Interference Coordination:
# 1: Area Coordination
# 2: Point Coordination
interference_coordination = 1

# Define Interference range for calculating IM in point interference coordination
I_max = 20
I_min = -96

# Define minimum rx power for calculating IM in area interference coordination
rx_power_min = -96  # dBm/10MHz, minimum Rx Power

# edge related
no_edge_distance = 40   # kilometer, the threshold of distance between 2 cbsd to have edge
initial_edge_threshold = 0.2    # 0~1, initialize the threshold of edge weight (ew) for edge creation

tx_power_min = 20   # dBm/10MHz, minimum Tx Power


# Channel Related
lb_channels_frequency = 3550     # MHz, the lower bound of frequency
hb_channels_frequency = 3700     # MHz, the lower bound of frequency

# zoning related
# degree_per_zone_latitude = 0.5      #
# degree_per_zone_longitude_low = 0.5     # degree

# Coloring related
max_attempt = 80        # Maximum attempt times for coloring
