import time, os
import app3_repeat_ew as ew
import app3_rp_data as dt
import app3_rp_eval as ev

cxg_select = "cxg_4/"

def cleanfile(infile):
    rawfix = "sameseed/repeat/ew/" + cxg_select
    noisefix = "sameseed/repeat/plot/app3/" + cxg_select

    postfixes = [".cbsd", ".area", ".ewt", ".cvg"]
    for ps in postfixes:
        filename = rawfix + infile + ps
        if os.path.exists(filename):
            os.remove(filename)
        else:
            print("The file does not exist")
    filename = noisefix + infile + "_app3.noise"
    if os.path.exists(filename):
        os.remove(filename)
    else:
        print("The file does not exist")

if __name__ == '__main__':
    densities = [10]
    locations = ["vb", "sd"]
    cats = ["both"]
    pms = ["hybrid", "itm"]
    seeds = range(98, 501)

    for mysd in seeds:
        for density in densities:
            for location in locations:
                for strcat in cats:
                    for pm in pms:
                        myinput = location + "_" + str(density) + "_" + strcat + "_" + pm
                        myoutput = str(density) + "/" + location + "_" + str(density) + "_" + strcat + "_" + pm + "_" + str(mysd)

                        print "Start Processing...", location+"-"+str(density)+"-"+strcat+"-"+pm+"-"+str(mysd)
                        start1 = time.time()
                        ew.diffseed(myinput, myoutput, pm, mysd)
                        stop = time.time()
                        print "EW Done! in", "{0:.4f}".format(stop-start1), "seconds"

                        start2 = time.time()
                        dt.plot_data_gen(str(density) + "/" + location + "_" + str(density) + "_" + strcat + "_" + pm + "_" + str(mysd))
                        stop = time.time()
                        print "BW, raw Noise Done! in", "{0:.4f}".format(stop - start2), "seconds"

                        start3 = time.time()
                        ev.plot_data(str(density) + "/" + location + "_" + str(density) + "_" + strcat + "_" + pm + "_" + str(mysd))
                        stop = time.time()
                        print "Ix Done! in", "{0:.4f}".format(stop - start3), "seconds"

                        stop = time.time()

                        print location+"-"+str(density)+"-"+strcat+"-"+pm+"-"+str(mysd), "Done! in", "{0:.4f}".format(stop-start1), "seconds"

                        cleanfile(str(density) + "/" + location + "_" + str(density) + "_" + strcat + "_" + pm + "_" + str(mysd))

                        print "File Cleaned"
                        print
