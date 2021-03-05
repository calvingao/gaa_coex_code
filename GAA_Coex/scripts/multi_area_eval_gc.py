import time
from gaa_sas import SAS


def gc(inputfile, outputfile):

    input_folder = "experiment/multi/ew/"
    output_folder = "experiment/multi/gc/"

    for set_cxg in [True]:

        # cxg_fix = "cxg_y/" if set_cxg else "cxg_n/"
        cxg_fix = ""

        infile = input_folder + cxg_fix + inputfile
        outfile = output_folder + cxg_fix + outputfile

        mysas = SAS()
        mysas.import_states(infile)

        mysas.graph_coloring_all_until_satisfied()

        mysas.export_states(outfile)
        mysas.export_cs(outfile)


if __name__ == '__main__':
    # densities = [3, 10, 30]
    # locations = ["vb", "sd"]
    # cats = ["_cata", "_both"]
    # pms = ["_itm", "_hybrid"]

    densities = [10]
    locations = ["sd"]
    cats = ["_both"]
    pms = ["_hybrid"]
    indexs = range(50)

    for density in densities:
        for location in locations:
            for strcat in cats:
                for pm in pms:
                    for index in indexs:

                        myinput = location + "_" + str(density) + strcat + pm + "_" + str(index) + "-1"
                        myoutput = location + "_" + str(density) + strcat + pm + "_" + str(index)

                        start = time.time()
                        gc(myinput, myoutput)
                        stop = time.time()

                        print location+str(density)+strcat+pm+str(index), "Done! in", stop-start, "seconds"
