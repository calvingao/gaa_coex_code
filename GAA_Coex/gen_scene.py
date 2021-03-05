import copy
import gaa_scenario as sc
import multiprocessing as mp


def create((density, location, cat)):

    # import default parameters
    param = copy.deepcopy(sc.DefaultParam.Param)
    param["CBSD_density"] = density
    param["length_area"] = 5.0
    param["width_area"] = 5.0

    if location == "vb":
        param["lat_centroid"] = 36.842491   # 36.872227
        param["lon_centroid"] = -76.006384  # -76.023389

    if location == "sd":
        param["lat_centroid"] = 32.723588
        param["lon_centroid"] = -117.145319

    if cat == 1:
        param["cata_ratio_dense_urban"] = 0.9
        param["cata_ratio_urban"] = 0.9
        param["cata_ratio_suburban"] = 0.9
        param["cata_ratio_rural"] = 0.95
        strcat = "_both"
    else:
        strcat = "_cata"

    output_filename = "sameseed/scene/" + location + "_" + str(density) + strcat + ".list"

    CBSDs = sc.create(param, fix_seed=True, water_deploy=True)
    CBSDs = sc.cxg_assign(CBSDs, num_of_cxg=3)

    sc.fileout(output_filename, param, CBSDs)

    return CBSDs


if __name__ == '__main__':

    densities = [3, 10, 30, 50]
    locations = ["vb", "sd"]
    cats = [1]

    tuples = []
    for den in densities:
        for loc in locations:
            for c in cats:
                tp = (den, loc, c)
                tuples.append(tp)
                print tp

    print len(tuples)

    p = mp.Pool(mp.cpu_count())

    ret = p.map(create, tuples)

    for item in ret:
        print len(item)
