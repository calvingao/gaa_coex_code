from gaa_sas import SAS
import gaa_evaluation as eval
import time


def plot_data_gen(loc, den, cat, pm):
    infile = loc + "_" + str(den) + "_" + cat + "_" + pm
    # infix = "experiment/plot/raw/compare/"
    # outfix = "experiment/plot/raw/compare/figures/"
    infix = "experiment/plot/test/compare/"
    outfix = "experiment/plot/test/compare/figures/"

    outfile = infile

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

    app1_bw = eval.load_content(infix + infile + "_app1.bw")
    # keys for .get()
    # "avg_bw_actual":  one value for Avg. Bandwidth per CBSD
    # "cdf_bw_actual":  cdf for Avg. BW

    bwcdf_data.append(app1_bw.get("cdf_bw_actual"))
    bwcdf_legend.append("Approach_1")
    bwcdf_style.append(("solid", 0))

    app1_ixic = eval.load_content(infix + infile + "_app1.ixic")
    # keys for .get()
    # "dbm_per_ch": cdf for Avg. inter-CxG ix
    # "avg_ix_per_ch_per_cbsd": one value for Avg. inter-CxG ix per CBSD
    # "max_noises": cdf for Max. inter-CxG ix
    # "min_noises": cdf for Min. inter-CxG ix

    ixiccdf_data.append(app1_ixic.get("dbm_per_ch"))
    ixiccdf_legend.append("Approach_1: Avg")
    ixiccdf_style.append(("solid", 0))

    ixiccdf_data.append(app1_ixic.get("max_noises"))
    ixiccdf_legend.append("Approach_1: Max")
    ixiccdf_style.append(("solid", 1))

    ixiccdf_data.append(app1_ixic.get("min_noises"))
    ixiccdf_legend.append("Approach_1: Min")
    ixiccdf_style.append(("solid", 2))

    bwix_data.append([(app1_ixic.get("avg_ix_per_ch_per_cbsd"), app1_bw.get("avg_bw_actual"), "ETWF")])
    bwix_legend.append("Approach_1")
    bwix_style.append(("solid", 0))

    app3_bwix_data = []
    for et in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        app3_bw = eval.load_content(infix + infile + "_app3_"+str(et)+".bw")
        # keys for .get()
        # "et": et,
        #  "cdf_bw_max": cdf for Max_BW
        #  "avg_bw_max": one value for Avg. Max_BW per CBSD
        bwcdf_data.append(app3_bw.get("cdf_bw_max"))
        bwcdf_legend.append("Approach_3: ET="+str(app3_bw.get("et")))
        bwcdf_style.append(("dashed", int(et*10-1)))

        app3_ixic = eval.load_content(infix + infile + "_app3_"+str(et)+".ixic")
        # keys for .get()
        # "et": et,
        # "cdf_ix":     cdf for inter-CxG ix
        # "avg_ix_max": one value for Avg. inter-CxG ix per CBSD
        ixiccdf_data.append(app3_ixic.get("cdf_ix"))
        ixiccdf_legend.append("Approach_3: ET=" + str(app3_ixic.get("et")))
        ixiccdf_style.append(("dashed", int(et*10-1)))

        app3_bwix_data.append((app3_ixic.get("avg_ix_max"),
                               app3_bw.get("avg_bw_max"),
                               "ET="+str(app3_bw.get("et"))
                               ))

    bwix_data.append(app3_bwix_data)
    bwix_legend.append("Approach_3")
    bwix_style.append(("dashed", 0))



    text_cdf_bw = {"title": "CDF of Max Bandwidth",
                   "xlabel": "Bandwidth (MHz)",
                   "ylabel": "Probability (in %)",
                   "xlim": (0, 90),
                   "ylim": (0, 110),
                   }

    text_cdf_ix = {"title": "CDF of Potential Interference",
                   "xlabel": "dbm",
                   "ylabel": "Probability (in %)",
                   "xlim": (-150, 0),
                   "ylim": (0, 110),
                   }

    text_bw_interference = {"xlabel": "Average Inter-CxG Interference per CBSD (dbm per channel)",
                            "ylabel": "Average Bandwidth per CBSD (MHz)",
                            "xlim": (-140, 0),
                            "ylim": (0, 90),
                            }

    eval.plot_cdf(bwcdf_data, bwcdf_legend, bwcdf_style, text_cdf_bw,
                  outfix + "bandwidth/" + outfile + "_compare_bw.png")

    eval.plot_cdf(ixiccdf_data, ixiccdf_legend, ixiccdf_style, text_cdf_ix,
                  outfix + "interference/" + outfile + "_compare_ix.png")

    eval.plot_bw_interfernce(bwix_data, bwix_legend, bwix_style, text_bw_interference,
                             outfix + "quality/" + outfile + "_compare_bwix.png")

    stop = time.time()

    print infile, "ready! in", "{0:.4f}".format(stop-start), "seconds"


if __name__ == '__main__':
    locations = ["sd", "vb"]
    cats = ["both"]
    # densities = [3, 10, 30, 50]
    densities = [50]
    pms = ["itm", "hybrid"]

    for den in densities:
        for pm in pms:
            for loc in locations:
                for cat in cats:
                    plot_data_gen(loc, den, cat, pm)
