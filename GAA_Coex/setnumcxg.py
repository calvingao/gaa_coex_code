from gaa_sas import SAS
import numpy as np
import time

def assign_cxg(filename):
    cxgs = [3]
    for cxg_select in cxgs:
        ewfix = "sameseed/ew/" + "cxg_4/"
        outfix = "sameseed/ew/cxg_" + str(cxg_select) + "/"

        outfile = infile = filename

        start = time.time()

        mysas = SAS()
        mysas.import_states(ewfix + infile)

        num_of_cbsds = len(mysas.CBSDs)
        np.random.seed(0)
        cxgs = np.random.choice(range(cxg_select), num_of_cbsds)

        for cbsd, cxg in zip(mysas.CBSDs, list(cxgs)):
            cbsd.set_cxg(cxg)

        mysas.export_states(outfix + outfile)

        stop = time.time()

        print infile, "cxg_"+str(cxg_select), "ready! in", "{0:.4f}".format(stop-start), "seconds"


if __name__ == '__main__':
    locations = ["sd", "vb"]
    cats = ["both"]
    densities = [3, 10, 30, 50]
    pms = ["itm", "hybrid"]


    for den in densities:
        filenames = []

        for pm in pms:
            for loc in locations:
                for cat in cats:
                    filenames.append(loc + "_" + str(den) + "_" + cat + "_" + pm)

        for fn in filenames:
            assign_cxg(fn)
