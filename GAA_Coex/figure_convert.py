import numpy as np
from gaa_sas import SAS
from gaa_cbsd import CBSD
import json
import ndpool as mp
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from adjustText import adjust_text


colors = ["blue", "orange", "green", "red", "purple", "brown", "pink", "olive"]     # Color Map
min_rx = -96            # minimum rx signal
max_sir_value = 100     # sir is considered as this value, if above
channels_avail = 8      # available channels, default 8
total_num_grids = 10000     # Total number of grids of the araa, default 10000, (100*100)



def plot_origin_coverage(plotdata, text={}, outfile=""):
    """
    plot origin coverage map from given record file
    """
    content = plotdata

    cbsd_X = content.get("CBSDx")
    cbsd_Y = content.get("CBSDy")
    cbsd_C = content.get("CBSDc")
    cbsd_cat = content.get("CBSDcat")

    # cbsd_Color = [colors[x % 8] for x in cbsd_C]
    Coverage = content.get("coverage")

    for item in Coverage.values():
        xs = item.get("X")
        ys = item.get("Y")

        clrs = item.get("color")
        for clr in clrs:
            plt.scatter(xs, ys, s=20, c=colors[clr % 8], alpha=0.3, marker="s", lw=0)

    markers = []
    for x in cbsd_cat:
        if x == "cata":
            markers.append('^')
        else:
            markers.append('s')
    for i in range(len(cbsd_X)):
        plt.scatter(cbsd_X[i], cbsd_Y[i], s=50, c="white", marker=markers[i])

    plt.title(text.get("title"))
    plt.xlabel(text.get("xlabel"))
    plt.ylabel(text.get("ylabel"))
    plt.xlim(text.get("xlim"))
    plt.ylim(text.get("ylim"))

    # plt.show()
    plt.savefig(outfile)
    plt.close()


def plot_cdf(plotdatas, legends, text={}, outfile=""):
    """
    Plot CDF Figure given data_array and legends
    :type plotdatas:    List[float]
    :type legends:      List[String]
    :type text:         dict
    :type outfile:      str
    """
    content = "x\ty\tlegend"
    color_index=0
    for plotdata, legend in zip(plotdatas, legends):
        linestyle = "solid" if color_index%2==0 else "dashed"
        # Count Number of Nones
        Num_None = [v for v in plotdata if v is None].count(None)
        # x-value for all non-None value
        if Num_None != len(plotdata):
            Xs = [v for v in plotdata if v is not None]
            Xs.insert(0, Xs[0])
            Xs.append(text.get("xlim")[1])
            # percentage of total numbers
            Ys = [index/float(len(plotdata)) for index in range(Num_None+1, len(plotdata)+1)]
            Ys.insert(0, 0)
            Ys.append(Ys[-1])

            plt.plot(Xs, Ys, label=legend, c=colors[color_index/2], ls=linestyle, alpha=0.8)
            plt.legend(loc=0)
        else:
            plt.scatter(0, 0, label=legend)
        color_index += 1

    if text.get("title") is not None:
        plt.title(text.get("title"))
    plt.xlabel(text.get("xlabel"))
    plt.ylabel(text.get("ylabel"))
    plt.xlim(text.get("xlim"))
    plt.ylim(text.get("ylim"))
    plt.legend(loc=0, fontsize=12)
    # plt.show()
    plt.savefig(outfile)
    plt.close()


def plot_bw_interfernce(datas, legends, text={}, outfile=""):
    max_ix = text.get("xlim")[0]
    min_ix = text.get("xlim")[1]

    texts = []

    color_index = 0
    for data, legend in zip(datas, legends):
        linestyle = "solid" if color_index%2==0 else "dashed"
        marker = "s" if color_index%2==0 else "o"

        ixs, bws, ets = zip(*data)

        max_ix = max(max(ixs), max_ix)
        min_ix = min(min(ixs), min_ix)

        plt.scatter(ixs, bws, c=colors[color_index/2], marker=marker, alpha=0.8)
        plt.plot(ixs, bws, c=colors[color_index/2], label=legend, ls=linestyle)

        for ix, bw, et in zip(ixs, bws, ets):
            # plt.annotate(et, (ix, bw), textcoords="offset points", xytext=(3, -8), fontsize=8, ha='left')
            texts.append(plt.text(ix, bw, et, fontsize=8))

        color_index += 1

    if text.get("title") is not None:
        plt.title(text.get("title"))
    plt.xlabel(text.get("xlabel"))
    plt.ylabel(text.get("ylabel"))
    plt.xlim(float(int(min_ix/10)*10-10), float(int(max_ix/10)*10))
    plt.ylim(text.get("ylim"))
    plt.legend(loc=0, fontsize=12)

    adjust_text(texts, arrowprops=dict(arrowstyle="->", color='r', lw=0.5))

    # plt.show()
    plt.savefig(outfile)
    plt.close()


def plot_sir(plotdata, legend, channel, text={}, outfile=""):
    cbsd_X = plotdata.get("CBSDx")
    cbsd_Y = plotdata.get("CBSDy")
    cbsd_C = plotdata.get("CBSDc")
    cbsd_cat = plotdata.get("CBSDcat")
    markers = []
    for x in cbsd_cat:
        if x == "cata":
            markers.append('^')
        else:
            markers.append('s')

    # Mark CBSD use current channel as the channel color, otherwise white
    cbsd_Color = []
    for chs in cbsd_C:
        if channel in chs:
            cbsd_Color.append(colors[(channel-1) % 8])
        else:
            cbsd_Color.append("white")

    # SIR = plotdata.get("heatmap").get(channel)


    SIRs = {int(k): v for k, v in plotdata.get("heatmap").items()}
    SIR = SIRs.get(channel)

    if SIR is not None:
        X = [item.get("coordinate")[1] for item in SIR.values()]
        Y = [item.get("coordinate")[0] for item in SIR.values()]
        C = [item.get("sir") for item in SIR.values()]

        plt.scatter(X, Y, s=20, c=C, cmap="Spectral", marker="s", alpha=0.5, lw=0)
        plt.colorbar()

    for i in range(len(cbsd_X)):
        plt.scatter(cbsd_X[i], cbsd_Y[i], 50, c=cbsd_Color[i], marker=markers[i])

    plt.title("Signal to Interference Ratio for Channel " + str(channel) + "\n" + legend)
    plt.xlabel(text.get("xlabel"))
    plt.ylabel(text.get("ylabel"))
    plt.xlim(min(X), max(X))
    plt.ylim(min(Y), max(Y))
    plt.legend(loc=0, fontsize=12)

    # plt.show()
    plt.savefig(outfile)
    plt.close()





