import json

if __name__ == '__main__':
    locations = ["vb", "sd"]
    cats = ["cata", "both"]
    densities = [3, 10, 30, 50]
    pms = ["hybrid"]

    infix = "experiment/ew/tmp1/"
    ewfix = "experiment/ew/tmp2/"

    for den in densities:
        for loc in locations:
            for cat in cats:
                for pm in pms:
                    filename = loc + "_" + str(den) + "_" + cat + "_" + pm


                    f = open(infix+filename+".cvg")
                    content = json.load(f)  # type: dict

                    content1 = {k: val.popitem()[1] for k, val in content.items()}

                    # dict_items = [val for k, val in content.items()]
                    # content1 = {}
                    # for item in dict_items:
                    #     content1.update(item)

                    f2 = open(ewfix+filename+".cvg", "w")
                    json.dump(content1, f2)
                    print filename, "Done!"
