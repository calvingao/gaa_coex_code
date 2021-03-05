import gaa_evaluation as eval
import numpy as np

ets = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
target_cxg = "CxG_0"
sns = range(1, 151)

def get_bound(sd, n=len(sns)):
    return 1.96*sd/np.sqrt(n)

def get_linear(val_in_dbm):
    return np.power(10, val_in_dbm/10.0)

def get_db(val_in_linear):
    return np.log10(val_in_linear) * 10.0


def plot_data_gen(locs, cat, den, pms):
    infix = "experiment/plot/sameseed/repeat/" + str(den) + "/"

    for pm in pms:
        pm_txt = "ITM" if pm == "itm" else "Hybrid"

        print pm_txt+":"

        for loc in locs:
            loc_txt = "Virginia Beach" if loc == "vb" else "San Diego"
            print "\t"+loc_txt+":"

            ixval_by_et = {et: [] for et in ets}
            ixcov_by_et = {et: [] for et in ets}
            bw_by_et = {et: [] for et in ets}

            for sn in sns:
                infile = loc + "_" + str(den) + "_" + cat + "_" + pm + "_" + str(sn)

                # Inter-CxG BW
                app3_bw = eval.load_content(infix + infile + "_app3.cxgbw")

                # Inter-CxG Interference
                app3_ixic = eval.load_content(infix + infile + ".ixcovval")

                ix_coverage = app3_ixic.get("ix_coverage")
                noises = app3_ixic.get("noise")

                for et in ets:
                    bw_by_et[et].append(app3_bw.get(str(et)).get(target_cxg))
                    ixcov_by_et[et].append(ix_coverage.get(str(et)).get(target_cxg))
                    ixval_by_et[et].append(noises.get(str(et)).get(target_cxg))


            for et in ets:
                # print "\t\tET="+str(et)+":"

                # BW
                bw_all = bw_by_et.get(et)
                bw_mean = np.mean(bw_all)
                bw_sd = np.std(bw_all)
                bw_bound = get_bound(bw_sd)
                # print "\t\t\tAMABCC:\t\tMean =\t", "{0:.4f}".format(bw_mean), "\t\tSD =\t", "{0:.4f}".format(bw_sd), "\t\tSD/Mean = \t", "{0:.4f}".format(bw_sd/bw_mean*100)+"%", "\t\tBound_from_mean = \t", "{0:.4f}".format(bw_bound)


                # Ix Coverage
                ixcov_all = ixcov_by_et[et]
                ixcov_mean = np.mean(ixcov_all)
                ixcov_sd = np.std(ixcov_all)
                ixcov_bound = get_bound(ixcov_sd)
                # print "\t\t\tRCIAC:\t\tMean = \t", "{0:.4f}".format(ixcov_mean), "\t\tSD = \t", "{0:.4f}".format(ixcov_sd), "\t\tSD/Mean = \t", "{0:.4f}".format(ixcov_sd/ixcov_mean*100)+"%", "\t\tBound_from_mean = \t", "{0:.4f}".format(ixcov_bound)

                # Ix Value
                ixval_all_dbm = ixval_by_et.get(et)
                ixval_all_linear = [get_linear(v) for v in ixval_all_dbm]
                ixval_mean_linear = np.mean(ixval_all_linear)
                ixval_mean_dbm = get_db(ixval_mean_linear)

                ixval_sd_linear = np.std(ixval_all_linear)

                ixval_bound_linear = get_bound(ixval_sd_linear)
                ixval_bound_db = get_db(ixval_bound_linear/ixval_mean_linear + 1)
                # print "\t\t\tAAICIGC:\tMean(dbm) = \t", "{0:.4f}".format(ixval_mean_dbm), "\tBound_from_mean (db)= \t", "{0:.4f}".format(ixval_bound_db)
                print str(et), ",\t," ,\
                    "{0:.4f}".format(bw_mean), ",", \
                    "{0:.4f}".format(bw_sd), ",", \
                    "{0:.4f}".format(bw_sd / bw_mean * 100) + "%", ",", \
                    "{0:.4f}".format(bw_bound), \
                    ",\t,", \
                    "{0:.4f}".format(ixcov_mean), ",", \
                    "{0:.4f}".format(ixcov_sd), ",", \
                    "{0:.4f}".format(ixcov_sd/ixcov_mean*100)+"%", ",", \
                    "{0:.4f}".format(ixcov_bound), \
                    ",\t,", \
                    "{0:.4f}".format(ixval_mean_dbm), ",", \
                    "{0:.4f}".format(ixval_bound_db)



if __name__ == '__main__':
    locations = ["sd", "vb"]
    # locations = ["sd"]
    cat = "both"
    den = 10
    pms = ["hybrid", "itm"]

    plot_data_gen(locations, cat, den, pms)
