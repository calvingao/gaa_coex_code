from gaa_sas import SAS
import gaa_evaluation as eval
import json

if __name__ == '__main__':
    prefix = "experiment/journal/plotdata/"
    outfix = "experiment/journal/figures/"

    # locations = ["sd"]
    # cats = ["both"]
    locations = ["vb", "sd"]
    cats = ["both"]
    densities = [3, 10, 30, 50]
    pms = ["itm", "hybrid"]
    cxgs = ["cxg_n", "cxg_3", "cxg_4", "cxg_5"]

    stacks = ["10.0", "20.0", "30.0", "40.0", "50.0", "60.0", "70.0", "80.0"]

    for loc in locations:
        for cat in cats:
            for pm in pms:
                outfile = loc + "_" + pm

                loc_name = "Virginia Beach, VA" if loc == "vb" else "San Diego, CA"
                cat_name = "CatA CBSDs" if cat == "cata" else "Both CatA and CatB CBSDs"

                text_bar_bw = {
                               "xlabel": "Configurations",
                               "ylabel": "Percentage of CBSDs (in %)"
                               }

                legends_info = []
                data_bw_bars = []
                data_bw_histos = []

                for den in densities:
                    for cxg in cxgs:
                        cxg_txt = "w/ CxG" if cxgs.index(cxg) == 0 else "w/o CxG"
                        infile = loc + "_" + str(den) + "_" + cat + "_" + pm

                        legends_info.append("Density-" + str(den) + " " + cxg_txt)

                        data_bw = eval.load_content(prefix + cxg + "/" + infile + ".bwcdf")

                        data_bw_bars.append(data_bw.get("bw_cbsd_actual"))
                        # data_bw_histos.append(data_bw.get("cdf_bw_actual"))

                # eval.plot_bar(data_bw_bars, legends_info, stacks=stacks, text=text_bar_bw, outfile=outfix + outfile + "_bwcdf_bar.png")
                eval.plot_histo(data_bw_bars, legends_info, stacks=stacks, text=text_bar_bw, outfile=outfix + outfile + "_bwcdf_hist.png")
