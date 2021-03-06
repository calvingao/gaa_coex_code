from gaa_sas import SAS
import gaa_evaluation as eval
import numpy as np

min_rx = -96
ets = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


def plot_data_gen(filename):
    cxgs = ["cxg_4/"]
    for cxg_select in cxgs:
        ewfix = "sameseed/repeat/ew/" + cxg_select
        outfix = "sameseed/repeat/plot/app3/" + cxg_select
        outfile = infile = filename

        mysas = SAS()
        mysas.import_states(ewfix + infile)

        # Total Bandwidth
        Total_BandWidth = len(mysas.channels) * 10.0

        # Total CxG
        cxg_nums = {cbsd.CxG for cbsd in mysas.CBSDs}

        bw_content = {}
        for et in ets:
            # Max Bandwidth Assigned to each CBSD
            assignment = mysas.get_approach_3(et)
            bw_max_per_cbsd = {key: Total_BandWidth / val[0] for key, val in assignment.items()}

            tmp = {"CxG_" + str(cxg_num): np.mean([val for key, val in bw_max_per_cbsd.items()
                                                   if key in {cbsd.id for cbsd in mysas.CBSDs if cbsd.CxG == cxg_num}])
                   for cxg_num in cxg_nums}

            bw_content[str(et)] = tmp

        # print bw_content
        eval.save_content(bw_content, outfix + outfile + "_app3.cxgbw")
        print "bandwidth ready"


        potential_pairs_list = {et: mysas.get_approach_3(et) for et in ets}

        cxg_nums = {cbsd.CxG for cbsd in mysas.CBSDs}

        coverage = {}
        noises = {}
        for cxg_num in cxg_nums:
            noises_cxg = {}
            # find the coverage of all CBSDs in the CxG
            grids_covered = {key for cbsd in mysas.CBSDs if cbsd.CxG == cxg_num
                             for key, val in cbsd.coverage.items() if val >= min_rx}

            coverage["CxG_"+str(cxg_num)] = list(grids_covered)

            # for each grid, find the CBSDs cover and interfere it
            for grid_id in grids_covered:
                noises_grid = {}
                cbsds_in_cxg = {cbsd for cbsd in mysas.CBSDs if cbsd.CxG == cxg_num and cbsd.coverage.get(grid_id) >= min_rx}
                cbsds_out_cxg = {cbsd for cbsd in mysas.CBSDs if cbsd.CxG != cxg_num and cbsd.coverage.get(grid_id) >= min_rx}

                # under each edge threshold
                for et in ets:
                    noise_et = {}
                    potential_pairs = potential_pairs_list[et]      # {cbsd: (cluster_size, neighbors)}

                    for cbsd_out in cbsds_out_cxg:
                        # mark cbsd_out if has potential edges with any of the CBSD in the CxG
                        if any([cbsd_out.id in potential_pairs.get(cbsd_in.id)[1] for cbsd_in in cbsds_in_cxg]):
                            noise_et[cbsd_out.id] = cbsd_out.coverage.get(grid_id)

                    if len(noise_et) > 0:
                        noise_et["all"] = eval.get_per_unit_dbm(noise_et.values())      # Aggregated
                        noises_grid[str(et)] = noise_et
                if len(noises_grid) > 0:
                    noises_cxg[str(grid_id)] = noises_grid

            noises["CxG_"+str(cxg_num)] = noises_cxg if len(noises_cxg) > 0 else None

        eval.save_content({"noise": noises, "coverage": coverage, "grid": mysas.grids}, outfix + outfile + "_app3.noise")
        print "noise ready"


if __name__ == '__main__':
    densities = [10]
    locations = ["vb", "sd"]
    cats = ["both"]
    pms = ["hybrid", "itm"]
    seeds = range(1, 51)

    for den in densities:

        for pm in pms:
            for loc in locations:
                for cat in cats:
                    for seed in seeds:
                        plot_data_gen(loc + "_" + str(den) + "_" + cat + "_" + pm + "_" + str(seed))
