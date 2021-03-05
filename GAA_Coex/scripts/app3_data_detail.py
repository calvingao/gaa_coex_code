from gaa_sas import SAS
import gaa_evaluation as eval
import time

def plot_data_gen(filename):
    _text = ""
    cxgs = ["cxg_4/"]
    for cxg_select in cxgs:
        ewfix = "sameseed/ew/" + cxg_select
        infile = filename

        mysas = SAS()
        mysas.import_states(ewfix + infile)

        pairs = []  # type: List[Tuple[CBSD, CBSD]]
        all_cbsds = mysas.CBSDs.copy()
        while len(all_cbsds) >= 2:
            i = all_cbsds.pop()
            for j in all_cbsds:
                if i.CxG != j.CxG:
                    pairs.append((i, j))
        keyset = [frozenset((pair[0].id, pair[1].id)) for pair in pairs]


        for et in [0.1, 0.5, 0.9]:
            num_ew_intercxg = len([1 for key, val in mysas.ew_table.items() if key in keyset])
            num_edge_intercxg = len([1 for key, val in mysas.ew_table.items() if key in keyset and val > et])
            num_potential_ix_intercxg = len([1 for key, val in mysas.ew_table.items() if key in keyset and val <= et])
            # print "\tET=", et, "\tInter_CxG EW:",num_ew_intercxg, "\tInter_CxG Edge:", num_edge_intercxg, "\tInter_CxG Ix:", num_potential_ix_intercxg
            _text += "\tET= " + str(et) + ":\tInter_CxG EW: " + str(num_ew_intercxg) + "\tInter_CxG Edge: "\
                     + str(num_edge_intercxg) + "\tInter_CxG Ix: " + str(num_potential_ix_intercxg) + "\n"

    return _text



if __name__ == '__main__':
    locations = ["sd", "vb"]
    cats = ["both"]
    densities = [3, 10, 30, 50]
    pms = ["itm", "hybrid"]
    outfile = "compare_ew.txt"
    total_content = ""

    f = open(outfile, "w")
    f.write(total_content)
    f.close()

    for den in densities:
        content = ""
        filenames = []
        for pm in pms:
            start = time.time()
            # print "Density=", den,"\tPropagation:", pm
            content += "Density= " + str(den) + "\tPropagation: " + str(pm) + "\n"
            for loc in locations:
                fn = loc + "_" + str(den) + "_both_" + pm
                filenames.append(fn)
                # print "\t", loc, ":"
                content += "\t" + str(loc) + ":\n"
                content += plot_data_gen(fn)
                content += "\n"
            stop = time.time()
            print "Density=", str(den), ":", pm, " ready! in", "{0:.4f}".format(stop-start), "seconds"
        print content

        total_content += content
        f = open(outfile, "a")
        f.write(content)
        f.close()

    f1 = open("compare_all", "w")
    f1.write(total_content)
