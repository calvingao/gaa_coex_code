from gaa_sas import SAS
import gaa_evaluation as eval
import time
import matplotlib.pyplot as plt


min_rx = -96

# ets = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
ets = [0.1, 0.5, 0.9]

def plot_data(filename):
    cxgs = ["cxg_4/"]  #, "cxg_3/"]
    for cxg_select in cxgs:
        ewfix = "simpseed/ew/" + cxg_select
        infile = filename

        start = time.time()

        mysas = SAS()
        mysas.import_states(ewfix + infile)

        cbsds_1 = {cbsd for cbsd in mysas.CBSDs if cbsd.CxG == 1}

        for cbsd in cbsds_1:
            print cbsd.id, ":\t", len([val for val in cbsd.coverage.values() if val >= -96])
        color = ["red", "blue"]
        clr = 0
        for cbsd in mysas.CBSDs:
            if cbsd.id in ["36"]:
                cvg = {key for key in cbsd.coverage.keys() if cbsd.coverage.get(key) >= -96}
                coordinate = [mysas.grids.get(key) for key in cvg]
                if len(coordinate) > 0:
                    Ys, Xs = zip(*coordinate)
                    # Coverage[cbsd.id] = {"X": Xs, "Y": Ys, "color": clr}

                    plt.scatter(Xs, Ys, s=20, c=color[clr], alpha=0.3, marker="s", lw=0)
                    clr += 1

                plt.scatter(cbsd.longitude, cbsd.latitude, s=50, c="white", marker="^")

        lats = [x[1] for x in mysas.grids.values()]
        lons = [x[0] for x in mysas.grids.values()]
        plt.xlim(min(lats), max(lats))
        plt.ylim(min(lons), max(lons))
        # plt.savefig("simpseed/plot/" + outfile + ".png")
        plt.show()
        plt.close()

if __name__ == '__main__':
    locations = ["sd"]
    cats = ["both"]
    densities = [3]
    pms = ["hybrid"]

    for cat in cats:
        for pm in pms:
            print "Propagation:", pm
            for den in densities:
                print "Density=", den
                for loc in locations:
                    print loc, ":"
                    plot_data(loc + "_" + str(den) + "_" + cat + "_" + pm)
                    print


