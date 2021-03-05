import time
from gaa_sas import SAS


def ew(inputfile, outputfile, pm):

    input_folder = "sameseed/scene/"
    output_folder = "sameseed/ew/"

    cxg_fix = "cxg_4/"

    infile = input_folder + inputfile
    outfile = output_folder + cxg_fix + outputfile

    mysas = SAS(coordination="area", propagation=pm)
    mysas.load_CBSDs_file(infile)
    mysas.create_ew_table()
    mysas.export_states(outfile)



if __name__ == '__main__':
    # densities = [3, 10, 30, 50]
    densities = [50]
    # locations = ["vb", "sd"]
    locations = ["sd"]
    cats = ["_both"]
    pms = ["hybrid"]
    for density in densities:
        for location in locations:
            for strcat in cats:
                for pm in pms:
                    myinput = location + "_" + str(density) + strcat + ".list"
                    myoutput = location + "_" + str(density) + strcat + "_" + pm

                    start = time.time()
                    ew(myinput, myoutput, pm)
                    stop = time.time()

                    print location+str(density)+strcat+pm, "Done! in", stop-start, "seconds"
