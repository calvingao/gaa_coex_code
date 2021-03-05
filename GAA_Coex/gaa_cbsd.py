from typing import Set, Dict


# CBSD Related
class CBSD:
    """
    The CBSD object stores states of the CBSDs and provide operation methods
    """

    # Constructor
    def __init__(self, uid, lat, lon, height, max_power, region_type, indoor, cat):
        """
        This is the field of the CBSD object

        Input: (CBSD features, permanent in most cases)
            uid:
                unique identifier
                :type uid:  str

            latitude:
                latitude of the CBSD
                :type lat:  float

            longitude:
                longitude of the CBSD
                :type lon:  float

            height:
                height of the CBSD (AGL, above ground level)
                :type height:   float

            max_power:
                max transmitter power of the antenna
                :type max_power:    float

            region_type:
                "URBAN", "SUBURBAN", "RURAL"
                :type region_type:  str

        """
        # identifier
        self.id = uid       # type: str     # identifier of the CBSD

        # Coordinate
        self.latitude = lat     # type: float   # latitude
        self.longitude = lon    # type: float   # longitude
        self.region_type = region_type  # type: str     # "URBAN", "SUBURBAN", "RURAL"

        # Antenna
        self.antenna_cat = cat  # type: str     # "cata", "catb"
        self.indoor = indoor    # type: bool    # True for indoor, False for outdoor
        self.height = height    # type: float   # height (agl) of the antenna)
        self.TxPowerMax = max_power     # type: float   # Maximum transmitter power (eirp)
        self.TxPower = max_power        # type: float   # Actual transmitter power, initualized to max by default

        # Grouping
        # self.CS = 0         # type: int     # Connected Sets
        self.CxG = 0        # type: int     # Coexistence Group
        self.NEG = None     # Non-Edge Group        //Not in use for the current ver.
        self.CNG = None     # Common Node Group     //Not in use for the current ver.

        # Coverage
        self.coverage = None    # type: Dict[int: float]  # For Area Coordination Only, {grid_index: signal}

        # GAA Resource
        self.color = 0      # for coloring, 0 stands for unassigned, CxG-wide
        self.channels = set()  # type: Set[int] # Assigned Channels

    # Recover values from existing record
    def set_state(self, tx_power=None, color=0, cxg_id=0):
        """
        Set operation state of the CBSD, usually used for recovery from record file.

        Input:
            tx_power:
                actual transmitter power of the antenna
                default value equals to TxPowerMax (eirp)
                //reduced tx power only exists for temporary assignment at this stage // wgao 03-20-2019
                :type tx_power: float

            color:
                color assigned from graph coloring algorithm representing the resource assignment.
                Ranges [0, 15], default value is 0 for non-assigned
                :type color:    int

            # cs_id:
            #     id of the Connected Set the current CBSD belongs to.
            #     Default value 0 for unassigned (usually new-added) CBSD
            #     :type cs_id:      int

            cxg_id:
                id of the Coexistence Group the current CBSD belongs to.
                Default value 0 for singleton CBSD
                :type cxg_id:      int


        Pre-Conditions:
            CBSD object has been created.

        Post-Condition:
            Following fields of the object are set:
                self.TxPower
                self.color
                self.CS
                self.CxG
        """

        if tx_power is not None:
            self.set_power(tx_power)

        self.set_color(color)
        # self.set_cs(cs_id)
        self.set_cxg(cxg_id)

    # Set Coverage
    def set_coverage(self, coverage=None):
        self.coverage = coverage

    # Convert object to String value
    def get_state_content(self):
        """
        Covert CBSD state to output ready content for record to files.

        Pre-Condition:
            CBSD is created.

        Returns:
            dict of the values for each field.
        """
        info = {"id": self.id,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "agl": self.height,
                "eirp": self.TxPowerMax,
                "region_type": self.region_type,
                "indoor": self.indoor,
                "cat": self.antenna_cat,
                "tx_power": self.TxPower,
                "CxG": self.CxG
                }

        return info

    # Convert coverage map to json
    def get_coverage_content(self):
        """
        Covert coverage map to output ready content for record to files.

        Pre-Condition:
            CBSD coverage map is created

        Returns:
            dict of the coverage map, {cbsd_id: coverage}.
        """
        return self.coverage

    # Transmitter Power Related Methods:
    def set_power(self, power):
        """
        Set Transmitter Power in range [tx_power_min, TxPowerMax]

        Input:
            tx_power:
                actual transmitter power of the antenna
                default value equals to TxPowerMax (eirp)
                //reduced tx power only exists for temporary assignment at this stage // wgao 03-20-2019
                :type power: float
        """
        if power > self.TxPowerMax:
            self.TxPower = self.TxPowerMax
        # elif power < tx_power_min:
        #     self.TxPower = tx_power_min
        else:
            self.TxPower = power

    # Coloring Related Methods
    def set_color(self, color=0):
        """
        Set the color number

        Input:
            color:
                color assigned from graph coloring algorithm representing the resource assignment.
                Ranges [0, 15], default value is 0 for non-assigned
                :type color:    int
        """
        if color >= 0:
            self.color = color
        else:
            self.color = 0

    # Not Implemented yet, resource are represented by colors at this stage wgao 03-20-2019
    def set_channels(self, chs):
        """
        Allocate GAA resource (in form of set of channels) to this CBSD

        :type chs:  Set[int]
        :param chs: a set of bandwidth channels to allocate
        """
        self.channels = chs

    # # Grouping Related Methods:
    # def set_cs(self, cs_id=0):
    #     """
    #     Assign this CBSD to a Connected Set.
    #     The common use is to recover the information from record file.
    #
    #     Input:
    #         cs_id:
    #             id of the Connected Set the current CBSD belongs to.
    #             Default value 0 for unassigned (usually new-added) CBSD
    #             :type cs_id:      int
    #
    #     Post-condition:
    #         CBSD is assigned with a CS id
    #     """
    #     self.CS = cs_id
    #
    def set_cxg(self, cxg_id=0):
        """
        Assign this CBSD to a Coexistence Group.
        The common use is to recover the information record file.

        Input:
            cxg_id:
                id of the Coexistence Group the current CBSD belongs to.
                Default value 0 for singleton CBSD
                :type cxg_id:      int

        Post-condition:
            CBSD is assigned with a CxG id
        """
        self.CxG = cxg_id
