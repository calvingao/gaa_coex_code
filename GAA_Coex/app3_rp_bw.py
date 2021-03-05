from gaa_sas import SAS
import numpy as np
import gaa_evaluation as eval
import time


min_rx = -96
ets = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

def plot_data_gen(filename):
    cxgs = ["cxg_4/"]
    for cxg_select in cxgs:
        ewfix = "sameseed/repeat/ew/" + cxg_select
        outfix = "sameseed/repeat/plot/app3/" + cxg_select
        outfile = infile = filename

        start = time.time()
        mysas = SAS()
        mysas.import_states(ewfix + infile)

        # Total Bandwidth
        Total_BandWidth = len(mysas.channels) * 10.0

        # Total CxG
        cxg_nums = {cbsd.CxG for cbsd in mysas.CBSDs}

        bw_content = {}
        for et in ets:
            # Max Bandwidth Assigned to each CBSD
            assignment = mysas.get_approach_3(et)
            bw_max_per_cbsd = {key: Total_BandWidth / val[0] for key, val in assignment.items()}

            tmp = {"CxG_"+str(cxg_num): np.mean([val for key, val in bw_max_per_cbsd.items()
                                                 if key in {cbsd.id for cbsd in mysas.CBSDs if cbsd.CxG == cxg_num}])
                   for cxg_num in cxg_nums}

            bw_content[str(et)] = tmp

        # print bw_content
        eval.save_content(bw_content, outfix + outfile + "_app3.cxgbw")
        stop = time.time()

        print infile, cxg_select, "ready! in", "{0:.4f}".format(stop-start), "seconds"


if __name__ == '__main__':
    densities = [3]
    locations = ["vb", "sd"]
    cats = ["both"]
    pms = ["hybrid", "itm"]
    seeds = range(1, 51)

    for den in densities:

        for pm in pms:
            for loc in locations:
                for cat in cats:
                    for seed in seeds:
                        plot_data_gen(str(den) + "/" + loc + "_" + str(den) + "_" + cat + "_" + pm + "_" + str(seed))
