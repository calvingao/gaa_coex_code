from gaa_sas import SAS
import gaa_evaluation as eval
# import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import time

lines = ["-", "--", ":"]
colors = [0, 1, 2, 3]
ets = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
cxgs = [4, 3]
target_cxg = "CxG_0"


def plot_data_gen(locs, cats, dens, pms):
    infix = "experiment/plot/sameseed/"
    outfix = "experiment/plot/sameseed/figures/"

    for num_cxg in cxgs:
        cxg_folder = "cxg_" + str(num_cxg) + "/"
        outfile = "cxg_" + str(num_cxg)

        for cat in cats:

            bwset = []
            ix_value_set = []
            ix_coverage_set = []
            quality_value_set = []
            quality_coverage_set = []

            for pm in pms:
                pm_txt = "ITM" if pm == "itm" else "Hybrid"

                bwrow = []
                ix_value_row = []
                ix_coverage_row = []
                quality_value_row = []
                quality_coverage_row = []

                for den in dens:

                    bw_data = []
                    bw_legend = []
                    bw_style = []

                    ix_value_data = []
                    ix_coverage_data = []
                    ix_legend = []
                    ix_style = []

                    quality_value_data = []
                    quality_coverage_data = []


                    for loc in locs:
                        loc_txt = "Virginia Beach" if loc == "vb" else "San Diego"

                        infile = loc + "_" + str(den) + "_" + cat + "_" + pm
                        color = colors[locs.index(loc)]
                        ls = locs.index(loc)

                        # Bandwidth
                        app3_bw = eval.load_content(infix + cxg_folder + infile + "_app3.cxgbw")

                        bw_data.append([(et, app3_bw.get(str(et)).get(target_cxg)) for et in ets])
                        bw_legend.append(loc_txt)
                        bw_style.append((lines[ls % len(lines)], color))

                        # Inter-CxG Interference
                        app3_ixic = eval.load_content(infix + cxg_folder + infile + ".ixcovval")

                        ix_coverage = app3_ixic.get("ix_coverage")
                        noises = app3_ixic.get("noise")

                        ix_coverage_data.append([(et, ix_coverage.get(str(et)).get(target_cxg)) for et in ets[1:]])
                        ix_value_data.append([(et, noises.get(str(et)).get(target_cxg)) for et in ets[1:]])
                        ix_legend.append(loc_txt)
                        ix_style.append((lines[ls % len(lines)], color))

                        # Quality
                        quality_coverage_data.append([(app3_bw.get(str(et)).get(target_cxg),
                                                       ix_coverage.get(str(et)).get(target_cxg)) for et in ets[1:]])

                        quality_value_data.append([(app3_bw.get(str(et)).get(target_cxg),
                                                    noises.get(str(et)).get(target_cxg)) for et in ets[1:]])

                    bwrow.append((bw_data, bw_legend, bw_style, "Density=" + str(den) + ", " + pm_txt))
                    ix_coverage_row.append(
                        (ix_coverage_data, ix_legend, ix_style, "Density=" + str(den) + ", " + pm_txt))
                    ix_value_row.append((ix_value_data, ix_legend, ix_style, "Density=" + str(den) + ", " + pm_txt))
                    quality_coverage_row.append(
                        (quality_coverage_data, ix_legend, ix_style, "Density=" + str(den) + ", " + pm_txt))
                    quality_value_row.append(
                        (quality_value_data, ix_legend, ix_style, "Density=" + str(den) + ", " + pm_txt))

                bwset.append(bwrow)
                ix_coverage_set.append(ix_coverage_row)
                ix_value_set.append(ix_value_row)
                quality_coverage_set.append(quality_coverage_row)
                quality_value_set.append(quality_value_row)

            text_bar_bw = {
                "xlabel": "Edge Threshold",
                "ylabel": "AMABCC in " + target_cxg + " (MHz)",
                "xlim": (0.0, 1.0),
                "ylim": (0, 80),
                "figsize": (6, 8)
            }

            text_ix_coverage = {
                "xlabel": "Edge Threshold",
                "ylabel": "RCIAC of " + target_cxg + " (%)",
                "xlim": (0.0, 1.0),
                "ylim": (0, 110),
                "figsize": (6, 8)
            }

            text_ix_value = {
                "xlabel": "Edge Threshold",
                "ylabel": "AAICIGC of " + target_cxg + " (dbm)",
                "xlim": (0.0, 1.0),
                "ylim": (-100, -30),
                "figsize": (6, 8)
            }

            text_quality_coverage = {
                "xlabel": "Average Maxium Bandwidth Assigned",
                "ylabel": "Percentage of " + target_cxg + " Covered Area Interfered by other CxGs (%)",
                "xlim": (0.0, 80),
                "ylim": (0, 110),
                "figsize": (6, 8)
            }

            text_quality_value = {
                "xlabel": "Average Maxium Bandwidth Assigned",
                "ylabel": "Average Noise (dbm/10 MHz) from other CxGs of the Interfered Area in " + target_cxg,
                "xlim": (0.0, 80),
                "ylim": (-100, -30),
                "figsize": (6, 8)
            }

            eval.plot_group(bwset, text_bar_bw, outfix + "bandwidth/" + outfile + "_bw.png")
            eval.plot_group(ix_coverage_set, text_ix_coverage, outfix + "ix_coverage/" + outfile + "_ixcov.png")
            eval.plot_group(ix_value_set, text_ix_value, outfix + "ix_value/" + outfile + "_ixval.png")
            # eval.plot_group(quality_coverage_set, text_quality_coverage, outfix + "quality/" + outfile + "_qtcov.png")
            # eval.plot_group(quality_value_set, text_quality_value, outfix + "quality/" + outfile + "_qtval.png")

            print outfile, "ready!"


if __name__ == '__main__':
    locations = ["sd", "vb"]
    cats = ["both"]
    densities = [3, 10, 30, 50]
    pms = ["itm", "hybrid"]
    # locations = ["sd"]
    # cats = ["both"]
    # densities = [10]
    # pms = ["hybrid"]

    plot_data_gen(locations, cats, densities, pms)
