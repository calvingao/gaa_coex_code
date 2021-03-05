import gaa_evaluation as eval
lines = ["-", "--", ":", "-."]

if __name__ == '__main__':
    prefix = "experiment/multi/plotdata/"
    outfix = "experiment/multi/plot/"

    locations = ["sd"]
    cats = ["both"]
    densities = [10]
    pms = ["hybrid"]


    for loc in locations:
        for cat in cats:
            for den in densities:
                for pm in pms:

                    outfile = loc + "_" + str(den) + "_" + cat + "_" + pm

                    text_cdf_ix_worst = {"title": "Channel with Worst Interference",
                                         "xlabel": "AIPA (dBm)",
                                         "ylabel": "Probability",
                                         "xlim": (-140, 0),
                                         "ylim": (0, 110),
                                         }

                    legends = []
                    data_ix_cdf_worst = []
                    styles = []

                    for i in range(50):

                        infile = loc + "_" + str(den) + "_" + cat + "_" + pm + "_" + str(i)
                        legends.append("data:" + str(i))
                        styles.append((lines[i % 4], (i / 4)%10))

                        data_bw = eval.load_content(prefix + infile + ".bwcdf")
                        data_ix = eval.load_content(prefix + infile + ".ixcdf")

                        # data_bw_cdf.append(data_bw.get("cdf_bw_actual"))
                        data_ix_cdf_worst.append(data_ix.get("max_noises"))
                        # data_ix_cdf_best.append(data_ix.get("min_noises"))

                    # eval.plot_cdf(data_bw_cdf, legends_info, text=text_cdf_bw, outfile=outfix + outfile + "_bwcdf.png")
                    eval.plot_cdf(data_ix_cdf_worst, legends, styles, text=text_cdf_ix_worst, outfile=outfix + outfile + "_ixcdf_w.png")

