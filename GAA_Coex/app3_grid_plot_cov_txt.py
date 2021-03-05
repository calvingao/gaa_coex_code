
import json

colors = ["blue", "red", "orange", "green", "purple", "brown", "pink", "olive", "yellow", "cyan"]  # Color Map
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

            datatext = "x\ty\tlegend\n"

            for pm in pms:
                pm_txt = "ITM" if pm == "itm" else "Hybrid"

                for loc in locs:
                    loc_txt = "Virginia Beach" if loc == "vb" else "San Diego"

                    for den in dens:
                        infile = loc + "_" + str(den) + "_" + cat + "_" + pm

                        # Inter-CxG Interference
                        app3_ixic = load_content(infix + cxg_folder + infile + ".ixcovval")

                        datatext += "Density=" + str(den) + "\t" \
                                    + str(app3_ixic.get("signal_coverage").get(target_cxg) / 100.0) + "\t" \
                                    + loc_txt + " - " + pm_txt \
                                    + "\n"

            # output
            f = open(outfix + "coverage/" + outfile + "_coverage.txt", "w")
            f.write(datatext)

        # print outfile, "ready!"


def load_content(infile):
    f = open(infile)
    return json.load(f)


if __name__ == '__main__':
    locations = ["sd", "vb"]
    cats = ["both"]
    densities = [3, 10, 30, 50]
    pms = ["itm", "hybrid"]

    plot_data_gen(locations, cats, densities, pms)
