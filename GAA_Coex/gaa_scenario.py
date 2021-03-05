# Scenario Generator

import sys
import os
import json
import copy
import getopt
import numpy as np
import geopy
import geopy.distance as gd
from reference_models.geo import nlcd


class DefaultParam:
    """
    Defines Default Parameters to create CBSDs 
    
    """
    # Default Configuration File
    def __init__(self):
        pass

    cFile = "scenario.conf"
    # Default Output File
    oFile = "rawcbsds.list"

    Param = {
        #   CBSD density (per km2)
        "CBSD_density": 20,
        
        #   Centroid of the area in (lat, lon)
        "lat_centroid": 36.846849,
        "lon_centroid": -76.000229,

        #   length and width of the area (km)
        "length_area": 5,
        "width_area": 5,
        
        #   CBSD Antenna Types:
        #   Ratio of CatA CBSDs for each region type (in decimal, CatB will be (1 - ratio)
        "cata_ratio_dense_urban": 1.0,
        "cata_ratio_urban": 1.0,
        "cata_ratio_suburban": 1.0,
        "cata_ratio_rural": 1.0,
        
        #   Category A:
        #   Height Range (in meters)
        #       Dense URBAN:
        "cata_dense_urban_height_ratio": [0.5, 0.25, 0.25],
        "cata_dense_urban_height_low": [3, 18, 33],
        "cata_dense_urban_height_high": [15, 30, 60],

        #   Indoor Ratio
        #   Ratio of Indoor vs Outdoor
        #   Default: 100% for CatA and 0% for CatB
        "indoor_ratio_cata": 1,
        "indoor_ratio_catb": 0,
        
        #       URBAN:
        "cata_urban_height_ratio": [0.5, 0.5],
        "cata_urban_height_low": [3, 6],
        "cata_urban_height_high": [3, 18],
        
        #       SUBURBAN:
        "cata_suburban_height_ratio": [0.7, 0.3],
        "cata_suburban_height_low": [3, 6],
        "cata_suburban_height_high": [3, 12],
        
        #       RURAL:
        "cata_rural_height_ratio": [0.8, 0.2],
        "cata_rural_height_low": [3, 6],
        "cata_rural_height_high": [3, 6],
        
        #   EIRP Range (dBm/10MHz)
        #       Dense URBAN:
        "cata_dense_urban_eirp_low": 26,
        "cata_dense_urban_eirp_high": 26,
        
        #       URBAN:
        "cata_urban_eirp_low": 26,
        "cata_urban_eirp_high": 26,
        
        #       SUBURBAN:
        "cata_suburban_eirp_low": 26,
        "cata_suburban_eirp_high": 26,
        
        #       RURAL:
        "cata_rural_eirp_low": 26,
        "cata_rural_eirp_high": 26,
        
        
        #   Category B:
        #   Height Range (in meters)
        #       Dense URBAN:
        "catb_dense_urban_height_ratio": 1,
        "catb_dense_urban_height_low": 6,
        "catb_dense_urban_height_high": 30,
        #       URBAN:
        "catb_urban_height_ratio": 1,
        "catb_urban_height_low": 6,
        "catb_urban_height_high": 30,
        #       SUBURBAN: 
        "catb_suburban_height_ratio": 1,
        "catb_suburban_height_low": 6,
        "catb_suburban_height_high": 100,
        #       RURAL:
        "catb_rural_height_ratio": 1,
        "catb_rural_height_low": 6,
        "catb_rural_height_high": 100,
        
        #   EIRP Range (dBm/10MHz)
        #       Dense URBAN:
        "catb_dense_urban_eirp_low": 40,
        "catb_dense_urban_eirp_high": 47,
        #       URBAN:
        "catb_urban_eirp_low": 40,
        "catb_urban_eirp_high": 47,
        #       SUBURBAN:
        "catb_suburban_eirp_low": 47,
        "catb_suburban_eirp_high": 47,
        #       RURAL:
        "catb_rural_eirp_low": 47,
        "catb_rural_eirp_high": 47
    }


def create(param=copy.deepcopy(DefaultParam.Param), fix_seed=True, water_deploy=False):
    """
    Create CBSD deployment from given parameters

    Inputs:
        Parameters to create the scenario
        defined in DefaultParam

    Returns:
        A list of CBSD dictionary:
        (lat, lon, agl, eirp, region_type, antenna_type)
        lat, lon:       coordinate
        agl:            antenna's height above ground level
        eirp:           transmit power in dBm/10MHz
        region_type:    URBAN, SUBURBAN, RURAL
        antenna_type:   cata or catb
    """

    lat = param["lat_centroid"]         # latitude of the centroid
    lon = param["lon_centroid"]         # longitude of the centroid
    length = param["length_area"]      # length of the target area in km
    width = param["width_area"]       # width of the target area in km
    density = param["CBSD_density"]     # number of CBSDs per km2

    CBSDs = []

    size = int(length * width * density)

    # Generate Uniform Distributed
    # set same seed
    if fix_seed:
        np.random.seed(0)
    x = np.random.uniform(-width/2.0, width/2.0, size)
    y = np.random.uniform(-length/2.0, length/2.0, size)

    # Convert x/y in km to lat/lon
    lats, lons = getPoints(lat, lon, x, y)

    # Get region code from SAS National Land Cover Data for all lat/lon pairs
    region_codes = nlcd.NlcdDriver().GetLandCoverCodes(lats, lons)

    # Combine lat, lon with region code and exclude locations with region_code equals 11
    # region_code 11 represents open water according to NLCD.
    locations = zip(lats, lons, region_codes)

    if not water_deploy:
        locations = [a for a in locations if a[2] != 11]

    print "in water:", len([a for a in locations if a[2]==11]), "of", len(locations)

    # Generate CBSD tuples based on the profiles from Pre-defined parameters
    for location in locations:
        code = location[2]      # region code

        # Dense Urban (Type is set to URBAN as per NLCD)
        if code == 24:
            region_type = "URBAN"
            rw = "_dense_urban"     # region prefix
        # Urban
        elif code == 23:
            region_type = "URBAN"
            rw = "_urban"
        # SURBUBAN
        elif code == 22:
            region_type = "SUBURBAN"
            rw = "_suburban"
        # All other codes are considered as rural as per NLCD
        else:
            region_type = "RURAL"
            rw = "_rural"

        # Based on keywords from region type, choose pre-defined cata/catb ratio
        # cat = category prefix
        cata_ratio = param["cata_ratio"+rw]
        cat = np.random.choice(["cata", "catb"], p=[cata_ratio, 1-cata_ratio])

        # Based on category choose indoor
        prob_indoor = param["indoor_ratio_" + cat]
        indoor = np.random.choice([1, 0], p=[prob_indoor, 1-prob_indoor])

        # Based on region type and category, choose ratio and range of agl and eirp
        prob_height = param[cat + rw + "_height_ratio"]
        if np.isscalar(prob_height):
            tmp = prob_height
            prob_height = [tmp]

        height_low = param[cat + rw + "_height_low"]
        if np.isscalar(height_low):
            tmp = height_low
            height_low = [tmp]

        height_high = param[cat + rw + "_height_high"]
        if np.isscalar(height_high):
            tmp = height_high
            height_high = [tmp]

        eirp_low = param[cat + rw + "_eirp_low"]
        eirp_high = param[cat + rw + "_eirp_high"]


        i = np.random.choice(range(len(prob_height)), p=prob_height)
        agl = np.random.choice(range(int(height_low[i]), int(height_high[i])+1))
        eirp = np.random.choice(range(int(eirp_low), int(eirp_high)+1))

        # add CBSD as dictionary
        CBSD_dict = {"latitude": location[0],
                     "longitude": location[1],
                     "agl": agl, "eirp": eirp,
                     "region_type": region_type,
                     "indoor": bool(indoor),
                     "cat": cat
                     }
        # CBSD_tuple = (location[0], location[1], agl, eirp, region_type, indoor, cat)
        CBSDs.append(CBSD_dict)

    return CBSDs


def cxg_assign(cbsds, num_of_cxg=0, fix_seed=True):
    """
    Randomly Assign all CBSDs to given number of CxGs
    """
    num_of_cbsds = len(cbsds)
    if fix_seed:
        np.random.seed(0)
    cxgs = np.random.choice(range(num_of_cxg + 1), num_of_cbsds)
    for cbsd, cxg in zip(cbsds, list(cxgs)):
        cbsd["CxG"] = cxg

    return cbsds


# Convert x/y in km to lat/lon
def getPoints(lat0, lon0, x, y):
    """
    Convert x,y (in km) to lat,long with given (lat, lon) represents (0,0) in km

    Inputs:

        lat0, lon0:     coordinates of (0, 0) in km
        x, y (iterables such as list or ndarray): coordinates of points in km.

    Returns:
        the coordinate(s) in lat, lon
    """
    start = geopy.Point(lat0, lon0)
    points = []
    for _x, _y in zip(x, y):
        north = gd.VincentyDistance(kilometers=_y)
        east = gd.VincentyDistance(kilometers=_x)
        points.append(north.destination(east.destination(start, 90), 0))
    lats, lons = zip(*points)[:2]
    return lats, lons


def fileout(filename, param, CBSDs):
    """
    Output raw cbsd list to file, with plot
    :type filename: str
    :type param:    dict
    :type CBSDs:    List

    """

    # check and create directory
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # use sequence number to avoid overriding existing files
    fn = filename.split(".")
    if len(fn) >= 2:
        fname = ".".join(fn[:-1])
        fext = "." + fn[-1]
    else:
        fname = filename
        fext = ""

    index = 0
    outfile = fname + fext
    while os.path.exists(outfile):
        index += 1
        outfile = fname + "-" + str(index) + fext

    # # Scenario Profile:
    # Deployment Area
    area_dict = {
        "lat0": param["lat_centroid"],
        "lon0": param["lon_centroid"],
        "width": param["width_area"],
        "length": param["length_area"]
    }

    # CBSDs
    cbsds_list = []
    index = 1
    for item in CBSDs:
        item["id"] = str(index)
        cbsds_list.append(item)
        index += 1

    scenario = {"area": area_dict, "CBSDs": cbsds_list}

    f = open(outfile, "w")
    json.dump(scenario, f)

# Retrieve parameters from given configure file
def getParam(conf_file):
    # Loading default parameters
    myparam = copy.deepcopy(DefaultParam.Param)

    # Read from configuration file for parameters
    if os.path.exists(conf_file):
        print "Using configuration file:", conf_file
        f = open(conf_file, "r")
        for line in f:
            line.strip()
            if (line[0] not in ("#", "\n")) and (len(line) > 0) and ("=" in line):
                linestring = line.split("#", 2)[0]      # Fetch before "#"
                var_vals = linestring.split("=", 2)
                varstr = var_vals[0].strip()
                valstr = var_vals[1].strip().split(",")

                if len(valstr) == 1:
                    vals = float(valstr[0])
                    myparam[varstr] = vals

                else:
                    vals = []
                    for val in valstr:
                        vals.append(float(val))
                    myparam[varstr] = vals

        return myparam

    else:
        print "Configuration File", conf_file, "does not exist."
        return None


# Reading from infile for parameters and output to outfile
def main(argv):

    """
    Generating CBSD depolyments
    'python scenario.py -c <configuration file> -o <output file>'
    """

    # Set Default In/Out File
    confile = DefaultParam.cFile
    outputfile = DefaultParam.oFile

    # Get filename from command argv
    try:
        opts, args = getopt.getopt(argv, "hc:o:", ["cfile=", "ofile="])
    except getopt.GetoptError:
        print 'scenario.py -c <configuration file> -o <output file>'
        print ''
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'scenario.py -c <configuration file> -o <output file>'
            sys.exit()
        elif opt in ("-c", "--cfile"):
            confile = arg.strip()
        elif opt in ("-o", "--ofile"):
            outputfile = arg.strip()

    # Set Parameters
    myparam = getParam(confile)

    if myparam is None:
        print 'Scenario not created due to invalid configuration file.'
    else:
        # Create CBSDs based on configuration file
        CBSDs = create(myparam)
        # output result to files
        fileout("output/" + outputfile, myparam, CBSDs)


if __name__ == '__main__':
    main(sys.argv[1:])
    # param = DefaultParam.Param
    # res = create(param)
    # fileout("output/bbb.list", param, res)
