from gaa_sas import SAS
import gaa_evaluation as eval
import time


def plot_data_gen(filename):
    ewfix = gcfix = "experiment/multi/gc/"
    outfix = "experiment/multi/plotdata/"

    outfile = infile = filename

    start = time.time()

    mysas = SAS()
    mysas.import_states(ewfix + infile)
    mysas.import_cs(gcfix + infile)
    mysas.assign_channels()

    data_bw = eval.get_plotdata_bandwidth(mysas)
    data_ix = eval.get_plotdata_interference(mysas)

    eval.save_content(data_bw, outfix + outfile + ".bwcdf")
    eval.save_content(data_ix, outfix + outfile + ".ixcdf")

    stop = time.time()

    print infile, "ready! in", "{0:.4f}".format(stop-start), "seconds"


if __name__ == '__main__':

    locations = ["sd"]
    cats = ["both"]
    densities = [10]
    pms = ["hybrid"]

    filenames = []

    for den in densities:
        for pm in pms:
            for loc in locations:
                for cat in cats:
                    for i in range(50):
                        filenames.append(loc + "_" + str(den) + "_" + cat + "_" + pm + "_" + str(i))

    for fn in filenames:
        plot_data_gen(fn)
