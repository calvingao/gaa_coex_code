from gaa_sas import SAS
import gaa_evaluation as eval
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import time

colors = ["blue", "red", "orange", "green", "purple", "brown", "pink", "olive", "yellow", "cyan"]     # Color Map
hatches = ['', 'O', '//', '-', '+', 'x', 'o', '.', '*']
cxgs = [4, 3]
target_cxg = "CxG_0"


def plot_data_gen(locs, cats, dens, pms):
    infix = "experiment/plot/sameseed/"
    outfix = "experiment/plot/sameseed/figures/"

    for num_cxg in cxgs:
        cxg_folder = "cxg_" + str(num_cxg) + "/"
        outfile = "cxg_" + str(num_cxg)

        for cat in cats:

            labels = ["Density="+str(den) for den in dens]
            x = np.arange(len(labels))  # the label locations
            width = 0.17  # the width of the bars

            fig, ax = plt.subplots()
            rects = []
            pos = -width*1.5

            for pm in pms:
                pm_txt = "ITM" if pm == "itm" else "Hybrid"

                for loc in locs:
                    loc_txt = "Virginia Beach" if loc == "vb" else "San Diego"

                    data = []

                    for den in dens:
                        infile = loc + "_" + str(den) + "_" + cat + "_" + pm

                        # Inter-CxG Interference
                        app3_ixic = eval.load_content(infix + cxg_folder + infile + ".ixcovval")
                        data.append(app3_ixic.get("signal_coverage").get(target_cxg)/100.0)

                    rects.append(ax.bar(x + pos, data, width, label=loc_txt + " - " + pm_txt,
                                 color=colors[locs.index(loc)], edgecolor='white', hatch=hatches[pms.index(pm)]))

                    pos += width

            ax.set_ylabel("CRC of " + str(target_cxg) + " (%)")
            ax.set_xticks(x)
            ax.set_xticklabels(labels)
            ax.legend(loc="lower right")

            plt.ylim((0, 110))

            fig.tight_layout()

            # plt.show()
            plt.savefig(outfix + "coverage/" + outfile + "_coverage.png")

        print outfile, "ready!"


if __name__ == '__main__':
    locations = ["sd", "vb"]
    cats = ["both"]
    densities = [3, 10, 30, 50]
    pms = ["itm", "hybrid"]

    plot_data_gen(locations, cats, densities, pms)
