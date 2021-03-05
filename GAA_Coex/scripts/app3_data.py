from gaa_sas import SAS
import gaa_evaluation as eval
import time


def plot_data_gen(filename):
    cxgs = ["cxg_4/", "cxg_3/"]
    for cxg_select in cxgs:
        ewfix = "sameseed/ew/" + cxg_select
        outfix = "sameseed/plot/app3/" + cxg_select

        outfile = infile = filename

        start = time.time()

        mysas = SAS()
        mysas.import_states(ewfix + infile)
        # mysas.import_cs(gcfix + infile)
        # mysas.assign_channels()
        #
        # app1_bw = eval.get_plotdata_bandwidth(mysas)
        # app1_ix_ic = eval.get_plotdata_inter_cxg_ix_per_ch(mysas)
        #
        # eval.save_content(app1_bw, outfix + outfile + "_app1.bw")
        # # keys for .get()
        # # "avg_bw_actual":  one value for Avg. Bandwidth per CBSD
        # # "cdf_bw_actual":  cdf for Avg. BW
        #
        # eval.save_content(app1_ix_ic, outfix + outfile + "_app1.ixic")
        # # keys for .get()
        # # "dbm_per_ch": cdf for Avg. inter-CxG ix
        # # "avg_ix_per_ch_per_cbsd": one value for Avg. inter-CxG ix per CBSD
        # # "max_noises": cdf for Max. inter-CxG ix
        # # "min_noises": cdf for Min. inter-CxG ix

        for et in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:

            app3_bw = eval.get_bw_app3(mysas, et)
            app3_ix_ic = eval.get_ix_app3(mysas, et)

            eval.save_content(app3_bw, outfix + outfile + "_app3_"+str(et)+".bw")
            # keys for .get()
            # "et": et,
            #  "cdf_bw_max": cdf for Max_BW
            #  "avg_bw_max": one value for Avg. Max_BW per CBSD

            eval.save_content(app3_ix_ic, outfix + outfile + "_app3_"+str(et)+".ixic")
            # keys for .get()
            # "et": et,
            # "cdf_ix":     cdf for inter-CxG ix
            # "avg_ix_max": one value for Avg. inter-CxG ix per CBSD

        stop = time.time()

        print infile, cxg_select, "ready! in", "{0:.4f}".format(stop-start), "seconds"


if __name__ == '__main__':
    locations = ["sd", "vb"]
    cats = ["both"]
    densities = [3, 10, 30, 50]
    pms = ["itm", "hybrid"]

    for den in densities:
        filenames = []

        for pm in pms:
            for loc in locations:
                for cat in cats:
                    filenames.append(loc + "_" + str(den) + "_" + cat + "_" + pm)

        for fn in filenames:
            plot_data_gen(fn)
