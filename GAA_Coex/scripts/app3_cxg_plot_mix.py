from gaa_sas import SAS
import gaa_evaluation as eval
import time

lines = ["-", "--", ":"]
colors = [0, 1, 2, 3]
stacks = ["0.0", "20.0", "26.7", "40.0", "80.0"]

def plot_data_gen(locs, cats, dens, pms):
    infix = "experiment/plot/sameseed/"
    outfix = "experiment/plot/sameseed/figures/"

    cxgs = [3, 4]
    for num_cxg in cxgs:
        cxg_folder = "cxg_" + str(num_cxg) + "/"
        outfile = "cxg_" + str(num_cxg)

        for cat in cats:

            bwset = []
            ixset = []

            for pm in pms:
                pm_txt = "ITM" if pm == "itm" else "Hybrid"

                bwrow = []
                ixrow = []

                ets = [0.1, 0.5, 0.9]
                for et in ets:

                    bwcdf_data = []
                    bwcdf_legend = []
                    bwcdf_style = []

                    ixiccdf_data = []
                    ixiccdf_legend = []
                    ixiccdf_style = []

                    for den in dens:

                        color = colors[dens.index(den)]

                        for loc in locs:
                            infile = loc + "_" + str(den) + "_" + cat + "_" + pm
                            loc_txt = "Virginia Beach" if loc == "vb" else "San Diego"
                            ls = locs.index(loc)
                            app3_bw = eval.load_content(infix + cxg_folder + infile + "_app3_"+str(et)+".bw")
                            # keys for .get()
                            # "et": et,
                            #  "cdf_bw_max": cdf for Max_BW
                            #  "avg_bw_max": one value for Avg. Max_BW per CBSD
                            bw_percentages = {}
                            bw_raw = [str("{:.1f}".format(x)) for x in app3_bw.get("cdf_bw_max")]
                            for bw_val in stacks:
                                bw_percentages[bw_val] = bw_raw.count(bw_val) * 1.0 / len(bw_raw)
                            print bw_percentages
                            bwcdf_data.append(bw_percentages)
                            bwcdf_legend.append("Density=" + str(den) + ", " + loc_txt)
                            bwcdf_style.append((ls, color))


                            app3_ixic = eval.load_content(infix + cxg_folder + infile + "_app3_"+str(et)+".ixic")
                            # keys for .get()
                            # "et": et,
                            # "cdf_ix":     cdf for inter-CxG ix
                            # "avg_ix_max": one value for Avg. inter-CxG ix per CBSD
                            ixiccdf_data.append(app3_ixic.get("cdf_ix"))
                            ixiccdf_legend.append("Density=" + str(den) + ", " + loc_txt)
                            ixiccdf_style.append((lines[ls], color))

                    bwrow.append((bwcdf_data, bwcdf_legend, bwcdf_style, "ET=" + str(et) + ", " + pm_txt))
                    ixrow.append((ixiccdf_data, ixiccdf_legend, ixiccdf_style, "ET=" + str(et) + ", " + pm_txt))

                bwset.append(bwrow)
                ixset.append(ixrow)

            text_bar_bw = {
                "xlabel": "Configurations",
                "ylabel": "Percentage of CBSDs (in %)"
            }

            text_cdf_ix = {"title": "CDF of Potential Interference",
                           "xlabel": "dbm",
                           "ylabel": "Probability (in %)",
                           "xlim": (-150, -20),
                           "ylim": (0, 110),
                           }

            # eval.plot_group_histo(bwset, stacks, text_bar_bw,
            #                       outfix + "bandwidth_34/" + outfile + "_compare_bw.png")

            eval.plot_group_cdf(ixset, text_cdf_ix,
                                outfix + "coverage/" + outfile + "_compare_ix.png")

            print outfile, "ready!"


if __name__ == '__main__':
    locations = ["sd", "vb"]
    cats = ["both"]
    densities = [3, 10, 30, 50]
    pms = ["itm", "hybrid"]

    plot_data_gen(locations, cats, densities, pms)
    #
    # for den in densities:
    #     for pm in pms:
    #         for loc in locations:
    #             for cat in cats:
    #                 plot_data_gen(loc, den, cat, pm)
