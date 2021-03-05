from reference_models.geo import nlcd
import json
import matplotlib.pyplot as plt


def get_type(code):
    # Dense Urban, Urban
    if code == 24 or code == 23:
        region_type = "URBAN"
        color = "red"
    # SURBUBAN
    elif code == 22:
        region_type = "SUBURBAN"
        color = "orange"
    # Water
    elif code == 11:
        region_type = "WATER"
        color = "cyan"
    # All other codes are considered as rural as per NLCD
    else:
        region_type = "RURAL"
        color = "green"

    return region_type, color


def get_region(file):
    f = open(file)
    content = json.load(f)  # type: dict

    coordinate = content.values()

    lats, lons = zip(*coordinate)

    region_codes = nlcd.NlcdDriver().GetLandCoverCodes(lats, lons)

    rts, clrs = zip(*[get_type(code) for code in region_codes])

    return {"lat": lats, "lon": lons, "region": rts, "color": clrs}


def plot_region(data, title, outfile=""):
    """
    :type data: dict
    """
    lats = data.get("lat")
    lons = data.get("lon")
    colors = data.get("color")

    plt.scatter(lons, lats, c=colors, marker="s", alpha=0.5, lw=0)
    plt.title("Region Type in " + title)
    plt.xlim(min(lons), max(lons))
    plt.ylim(min(lats), max(lats))

    if outfile=="":
        plt.show()
    else:
        plt.savefig(outfile)
    plt.close()



if __name__ == '__main__':
    # vb = "experiment/ew/cxg_n/vb_1_both_hybrid.area"
    # sd = "experiment/ew/cxg_n/sd_1_both_hybrid.area"

    vb = "output/vb.clr"
    vb_name = "Virginia Beach, VA"
    sd = "output/sd.clr"
    sd_name = "San Diego, CA"

    f = open(vb)
    vb_data = json.load(f)

    f = open(sd)
    sd_data = json.load(f)

    plot_region(vb_data, vb_name, "vb.png")
    plot_region(sd_data, sd_name, "sd.png")

    # f = open("sd.clr", "w")
    # json.dump(get_region(sd), f)
