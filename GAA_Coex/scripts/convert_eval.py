import json

if __name__ == '__main__':
    locations = ["vb", "sd"]
    cats = ["cata", "both"]
    densities = [3, 10, 30]
    pms = ["itm", "hybrid"]

    for loc in locations:
        for cat in cats:

            infile = loc + "__" + cat

            f = open("output/plot/"+infile+".bwcdf")
            data_bw_cdf = json.load(f)  # type: list

            f = open("output/plot/"+infile+".ixcdf")
            data_ix_cdf = json.load(f)  # type: list

            f = open("output/plot/"+infile+".bwix")
            data_bw_ix = json.load(f)   # type: list

            f = open("output/plot/"+infile+".sir")
            data_sirs = json.load(f)    # type: list

            for den in densities:
                for pm in pms:
                    outfile = loc + "_" + str(den) + "_" + cat + "_" + pm

                    data_bw = data_bw_cdf.pop(0)    # get("cdf_bw_actual")
                    data_ix = data_ix_cdf.pop(0)    # get("min_noises")
                    data_bi = data_bw_ix.pop(0)
                    data_sir = data_sirs.pop(0)

                    f = open("output/plot/sep/"+outfile+".bwcdf", "w")
                    json.dump(data_bw, f)

                    f = open("output/plot/sep/"+outfile+".ixcdf", "w")
                    json.dump(data_ix, f)

                    f = open("output/plot/sep/"+outfile+".bwix", "w")
                    json.dump(data_bi, f)

                    f = open("output/plot/sep/"+outfile+".sir", "w")
                    json.dump(data_sir, f)

