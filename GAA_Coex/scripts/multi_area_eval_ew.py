import time
from gaa_sas import SAS


def ew(inputfile, outputfile):

    input_folder = "experiment/multi/scene/"
    output_folder = "experiment/multi/ew/"

    for set_cxg in [True]:

        # cxg_fix = "cxg_y/" if set_cxg else "cxg_n/"
        cxg_fix = ""
        infile = input_folder + inputfile
        outfile = output_folder + cxg_fix + outputfile

        mysas = SAS(coordination="area")
        mysas.load_CBSDs_file(infile)
        mysas.create_ew_table()

        mysas.export_states(outfile)



if __name__ == '__main__':
    densities = [10]
    locations = ["sd"]
    cats = ["_both"]
    pms = ["_hybrid"]
    indexs = range(50)

    # densities = [50]
    # locations = ["sd", "vb"]
    # cats = ["_cata", "_both"]
    # pms = ["_itm","_hybrid"]
    for density in densities:
        for location in locations:
            for strcat in cats:
                for pm in pms:
                    for index in indexs:
                        myinput = location + "_" + str(density) + strcat + "_" + str(index) + ".list"
                        myoutput = location + "_" + str(density) + strcat + pm + "_" + str(index)

                        start = time.time()
                        ew(myinput, myoutput)
                        stop = time.time()

                        print location+str(density)+strcat+pm, "Done! in", stop-start, "seconds"
