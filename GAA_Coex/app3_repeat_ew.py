import time, copy
import gaa_scenario as sc
from gaa_sas import SAS
import numpy as np


rts = ["URBAN", "SUBURBAN", "RURAL"]
rws = ["_urban", "_suburban", "_rural"]

def diffseed(inputfile, outputfile, pm, myseed):

    np.random.seed(myseed)
    input_folder = "sameseed/ew/"
    output_folder = "sameseed/repeat/ew/"

    cxg_fix = "cxg_4/"

    infile = input_folder + cxg_fix + inputfile
    outfile = output_folder + cxg_fix + outputfile

    param = copy.deepcopy(sc.DefaultParam.Param)

    mysas = SAS(coordination="area", propagation=pm)
    mysas.import_states(infile)


    for cbsd in mysas.CBSDs:        # Reset agl and eirp
        rw = rws[rts.index(cbsd.region_type)]
        cat = cbsd.antenna_cat

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
        agl = np.random.choice(range(int(height_low[i]), int(height_high[i]) + 1))
        eirp = np.random.choice(range(int(eirp_low), int(eirp_high) + 1))

        cbsd.height = agl
        cbsd.set_power(eirp)

    mysas.create_ew_table()
    mysas.export_states(outfile)



if __name__ == '__main__':
    densities = [10]
    locations = ["vb", "sd"]
    cats = ["both"]
    pms = ["hybrid", "itm"]
    seeds = range(1, 51)

    for density in densities:
        for location in locations:
            for strcat in cats:
                for pm in pms:
                    for mysd in seeds:
                        myinput = location + "_" + str(density) + "_" + strcat + "_" + pm
                        myoutput = location + "_" + str(density) + "_" + strcat + "_" + pm + "_" + str(mysd)

                        start = time.time()
                        diffseed(myinput, myoutput, pm, mysd)
                        stop = time.time()

                        print location+"-"+str(density)+"-"+strcat+"-"+pm+"-"+str(mysd), "Done! in", stop-start, "seconds"
