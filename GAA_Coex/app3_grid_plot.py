from gaa_sas import SAS
import gaa_evaluation as eval
import time

lines = ["-", "--", ":"]
colors = [0, 1, 2, 3]


def plot_data(locs, cats, dens, pms):

    infix = "experiment/plot/sameseed/"
    outfix = "experiment/plot/sameseed/figures/"


    for cat in cats:
        for pm in pms:
            for loc in locs:

                start = time.time()

                bwcdf_data = []
                bwcdf_legend = []
                bwcdf_style = []

                ixiccdf_data = []
                ixiccdf_legend = []
                ixiccdf_style = []

                bwix_data = []
                bwix_legend = []
                bwix_style = []

                for den in dens:
                    infile = loc + "_" + str(den) + "_" + cat + "_" + pm
                    color = colors[dens.index(den)]

                    cxgs = [3, 4]
                    for num_cxg in cxgs:
                        cxg_folder = "cxg_" + str(num_cxg) + "/"
                        ls = lines[cxgs.index(num_cxg)]

                        app3_bwix_data = []
                        for et in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
                            app3_bw = eval.load_content(infix + cxg_folder + infile + "_app3_"+str(et)+".bw")
                            # keys for .get()
                            # "et": et,
                            #  "cdf_bw_max": cdf for Max_BW
                            #  "avg_bw_max": one value for Avg. Max_BW per CBSD
                            # bwcdf_data.append(app3_bw.get("cdf_bw_max"))
                            # bwcdf_legend.append("Approach_3: ET="+str(app3_bw.get("et")))
                            # bwcdf_style.append(("dashed", int(et*10-1)))

                            app3_ixic = eval.load_content(infix + cxg_folder + infile + "_app3_"+str(et)+".ixic")
                            # keys for .get()
                            # "et": et,
                            # "cdf_ix":     cdf for inter-CxG ix
                            # "avg_ix_max": one value for Avg. inter-CxG ix per CBSD
                            # ixiccdf_data.append(app3_ixic.get("cdf_ix"))
                            # ixiccdf_legend.append("Approach_3: ET=" + str(app3_ixic.get("et")))
                            # ixiccdf_style.append(("dashed", int(et*10-1)))

                            app3_bwix_data.append((app3_ixic.get("avg_ix_max"),
                                                   app3_bw.get("avg_bw_max"),
                                                   "ET="+str(app3_bw.get("et"))
                                                   ))

                        bwix_data.append(app3_bwix_data)
                        bwix_legend.append(str(num_cxg) + " CxGs, Density " + str(den))
                        bwix_style.append((ls, color))



    # text_cdf_bw = {"title": "CDF of Max Bandwidth",
    #                "xlabel": "Bandwidth (MHz)",
    #                "ylabel": "Probability (in %)",
    #                "xlim": (0, 90),
    #                "ylim": (0, 110),
    #                }
    #
    # text_cdf_ix = {"title": "CDF of Potential Interference",
    #                "xlabel": "dbm",
    #                "ylabel": "Probability (in %)",
    #                "xlim": (-150, 0),
    #                "ylim": (0, 110),
    #                }

                text_bw_interference = {"xlabel": "Average Inter-CxG Interference per CBSD (dbm per channel)",
                                        "ylabel": "Average Bandwidth per CBSD (MHz)",
                                        "xlim": (-140, 0),
                                        "ylim": (0, 90),
                                        }

    # eval.plot_cdf(bwcdf_data, bwcdf_legend, bwcdf_style, text_cdf_bw,
    #               outfix + "bandwidth/" + outfile + "_compare_bw.png")
    #
    # eval.plot_cdf(ixiccdf_data, ixiccdf_legend, ixiccdf_style, text_cdf_ix,
    #               outfix + "interference/" + outfile + "_compare_ix.png")

                outfile_bwix = loc + "_" + pm

                eval.plot_bw_interfernce(bwix_data, bwix_legend, bwix_style, text_bw_interference,
                                         outfix + "quality_34/" + outfile_bwix + "_compare_bwix.png")

                stop = time.time()

                print outfile_bwix, "ready! in", "{0:.4f}".format(stop-start), "seconds"


if __name__ == '__main__':
    locations = ["sd", "vb"]
    cats = ["both"]
    densities = [3, 10, 30, 50]
    pms = ["itm", "hybrid"]

    plot_data(locations, cats, densities, pms)
