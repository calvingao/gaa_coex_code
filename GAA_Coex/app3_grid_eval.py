import gaa_evaluation as eval
import time

min_rx = -96

ets = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
# ets = [0.1, 0.5, 0.9]

def plot_data(filename):
    cxgs = ["cxg_4/", "cxg_3/"]
    for cxg_select in cxgs:
        infix = "sameseed/plot/app3/" + cxg_select
        outfix = infix
        # infix = "simpseed/plot/" + cxg_select
        infile = filename + "_app3.noise"

        start = time.time()

        content = eval.load_content(infix + infile)

        cxgs = content.get("coverage").keys()
        coverage = content.get("coverage")
        noises = content.get("noise")
        grids = content.get("grid")

        cov = {x for val in coverage.values() for x in val}
        # print "Coverage all CBSDS:", len(cov)



        ix_value_by_et = {}
        ix_coverage_by_et = {}

        signal_coverage = {target_cxg : len(coverage.get(target_cxg)) for target_cxg in cxgs}

        for et in ets:

            ix_value_by_cxg = {}
            ix_coverage_by_cxg = {}
            for target_cxg in cxgs:
                target_cxg_coverage = len(coverage.get(target_cxg))

                target_cxg_noises_map = {key: val.get(str(et)).get("all")
                                         for key, val in noises.get(target_cxg).items()
                                         if noises.get(target_cxg).get(key).get(str(et)) is not None}
                interfered_grids = len(target_cxg_noises_map) if target_cxg_noises_map is not None else 0
                avg_noise_level = eval.get_per_unit_dbm(target_cxg_noises_map.values(), interfered_grids * 1.0)

                ix_coverage_by_cxg[target_cxg] = interfered_grids * 100.0 / target_cxg_coverage
                ix_value_by_cxg[target_cxg] = avg_noise_level

            ix_coverage_by_et[str(et)] = ix_coverage_by_cxg
            ix_value_by_et[str(et)] = ix_value_by_cxg

        eval.save_content(
            {"signal_coverage": signal_coverage, "ix_coverage": ix_coverage_by_et, "noise": ix_value_by_et},
            outfix + filename + ".ixcovval")
        stop = time.time()

        print infile, cxg_select, "ready! in", "{0:.4f}".format(stop-start), "seconds"


if __name__ == '__main__':
    locations = ["sd", "vb"]
    cats = ["both"]
    densities = [3, 10, 30, 50]
    pms = ["itm", "hybrid"]

    for cat in cats:
        for pm in pms:
            print "Propagation:", pm
            for den in densities:
                print "Density=", den
                for loc in locations:
                    print loc, ":"
                    plot_data(loc + "_" + str(den) + "_" + cat + "_" + pm)
                    print


