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


def get_channel_util(mysas):
    channel_util = {}

    for ch in range(1, 1 + channels_avail):
        num_cbsds_in_ch = sum(ch in cbsd.channels for cbsd in mysas.CBSDs)
        channel_util[str(ch)] = float(num_cbsds_in_ch)/float(len(mysas.CBSDs))

    return channel_util


def get_plotdata_bandwidth(mysas):
    """
    Output Bandwidth Assignment Data of all CBSDs from given SAS

    Input:
            mysas:  SAS object
                :type mysas: SAS

    Return:
           avg_bw_actual, bw_cdf_actual, bw_actual, avg_bw_theoretical, bw_cdf_theoretical, bw_theoretical
    """
    # Total Bandwidth
    Total_BandWidth = len(mysas.channels) * 10.0

    # Total Number of CBSDs
    Total_CBSDs = len(mysas.CBSDs)

    # Actual Bandwidth Assigned to each CBSD (10, 20, ... , MHz)
    actual_bw_per_cbsd = {cbsd.id: (len(cbsd.channels) * 10.0) for cbsd in mysas.CBSDs}

    # cdf of actual bandwidth
    bw_cdf_actual = actual_bw_per_cbsd.values()
    bw_cdf_actual.sort()

    # Theoretical Bandwidth Assignment (Not necessary to be entire channels)
    theoretical_bw_per_cbsd = {}
    for cs in mysas.CSs:
        chromatic_cs = cs.get("chromatic")
        avg_bw = {cbsd_id: (Total_BandWidth/chromatic_cs) for cbsd_id in cs.get("members").keys()}
        theoretical_bw_per_cbsd.update(avg_bw)

    # cdf of theoretical bandwidth
    bw_cdf_theoretical = theoretical_bw_per_cbsd.values()
    bw_cdf_theoretical.sort()

    # Generate bar plotdata for actual bandwidth assignment
    # bandwitdh : percentage of cbsds (for bar plot)
    distinct_bw_actual = set(actual_bw_per_cbsd.values())
    bw_actual = {}
    for bw in distinct_bw_actual:
        percentage_cbsds = float(len({key for key, val in actual_bw_per_cbsd.items() if val == bw})) / Total_CBSDs
        bw_actual.update({bw: percentage_cbsds})


    avg_bw_actual = sum(actual_bw_per_cbsd.values()) / Total_CBSDs

    # Generate bar plotdata for theoretical bandwidth assignment
    distinct_bw_theoretical = set(theoretical_bw_per_cbsd.values())
    bw_theoretical = {}
    for bw in distinct_bw_theoretical:
        percentage_cbsds = float(len({key for key, val in theoretical_bw_per_cbsd.items() if val == bw})) / Total_CBSDs
        bw_theoretical.update({bw: percentage_cbsds})

    avg_bw_theoretical = sum(theoretical_bw_per_cbsd.values()) / Total_CBSDs

    ret = {"avg_bw_actual": avg_bw_actual,
           "avg_bw_theoretical": avg_bw_theoretical,
           "cdf_bw_actual": bw_cdf_actual,
           "cdf_bw_theoretical": bw_cdf_theoretical,
           "bw_cbsd_actual": bw_actual,
           "bw_cbsd_theoretical": bw_theoretical
           }

    return ret


def get_per_unit_dbm(ixs, units=1.0):
    """
    Get accumulated dbm of a list of dbms
    Input:
            ixs:  list of interferences in dbm
                :type ixs: list
            units:  total number of units
                :type units: float

    Return:
            sum of ixs
    """
    if np.isscalar(ixs):
        ixs = [ixs]
    ixs = [x for x in ixs if x is not None]
    if len(ixs) > 0:
        sum_ix_in_linear = np.sum([np.power(10, np.divide(ixs, 10.0))])
        return np.log10(sum_ix_in_linear/float(units)) * 10.0
    else:
        return None


def get_ix_cbsd((cbsd, mysas)):
    """
    Get AIPA Noise for each CBSD with best and worst channel

    Input:
            sas:  SAS object
                :type mysas: SAS
            cbsd: CBSD object
                :type cbsd: CBSD

    Return:
            max_noise, min_noise, accu_noise
    """

    covered_grids = {key for key in cbsd.coverage.keys() if cbsd.coverage.get(key) >= min_rx}

    channel_noises = {}
    interference_all_channels = []

    # Each Channel
    for ch in cbsd.channels:
        # Find the interference from all other cbsds that use same channel
        interference_in_coverage = []
        for grid in covered_grids:
            interference_in_grid = [other_cbsd.coverage.get(grid)
                                    for other_cbsd in mysas.CBSDs
                                    if (other_cbsd.id != cbsd.id            # exclude self
                                        and ch in other_cbsd.channels       # Using same channel
                                        and other_cbsd.coverage.get(grid) >= min_rx)    # Above Threshold
                                    ]

            # Update list of each interference
            if len(interference_in_grid) > 0:
                interference_in_coverage.extend(interference_in_grid)
                interference_all_channels.extend(interference_in_grid)

        # if there are interferences over min_rx (-96dbm by default), calculate effective interferences
        # otherwise set channel noise to None
        channel_noises[ch] = get_per_unit_dbm(interference_in_coverage, len(covered_grids)) \
            if len(interference_in_coverage) > 0 else None

    # calculate sum of interference of all channel in each grid
    accumulated_ix_all_chs = get_per_unit_dbm(interference_all_channels) \
        if len(interference_all_channels) > 0 else None

    return max(channel_noises.values()), min(channel_noises.values()), accumulated_ix_all_chs


def get_plotdata_ix_per_ch(mysas):
    """
    Output per channel interference Data of all CBSDs from given SAS

    Input:
            mysas:  SAS object
                :type mysas: SAS

    Return:
           sorted dbm_per_channel of each cbsd
    """
    avg_dbm_per_ch = [get_per_unit_dbm([get_ix_cbsd((cbsd, mysas))[2]],
                                       len(cbsd.channels) * len({key for key in cbsd.coverage.keys()
                                                                 if cbsd.coverage.get(key) >= min_rx
                                                                 })
                                       )
                      for cbsd in mysas.CBSDs]

    avg_dbm_per_ch.sort()

    return {"dbm_per_ch": avg_dbm_per_ch}


def get_plotdata_interference(mysas):
    """
    Output Interference data of all CBSDs from given SAS

    Input:
            mysas:  SAS object
                :type mysas: SAS

    Return:
            CDF Plot Data for interference
    """
    cbsd_noises_max = {}
    cbsd_noises_min = {}

    ret = [get_ix_cbsd((cbsd, mysas)) for cbsd in mysas.CBSDs]

    maxns, minns, accumulated_noises = zip(*ret)

    for cbsd, max_noise, min_noise in zip(mysas.CBSDs, maxns, minns):
        cbsd_noises_max[cbsd] = max_noise
        cbsd_noises_min[cbsd] = min_noise

    max_noises = cbsd_noises_max.values()
    max_noises.sort()
    min_noises = cbsd_noises_min.values()
    min_noises.sort()

    overall_effective_interference_dbm = get_per_unit_dbm(accumulated_noises,
                                                          total_num_grids * channels_avail * len(mysas.CBSDs)
                                                          ) if len(accumulated_noises) > 0 else None

    result = {"max_noises": max_noises, "min_noises": min_noises, "overall_noises": overall_effective_interference_dbm}
    return result


def get_plotdata_sir(mysas):
    """
    Output SIR Data of all grids from given SAS

    Input:
            mysas:  SAS object
                :type mysas: SAS

    Return:
            SIR Plot data
    """
    Data = {}

    # Each Channel:
    for ch in mysas.channels:
        SIR = {}    # Ratio of Primary Signal vs Interference
        for grid_id in mysas.grids.keys():
            # Find CBSD Signals to the grid at given channel
            signals = [cbsd.coverage.get(grid_id)
                       for cbsd in mysas.CBSDs
                       if ch in cbsd.channels
                       ]
            # Filter only signals above min_rx
            signals = [x for x in signals if x is not None and x >= min_rx]

            # Check number of signals
            if len(signals) > 0:
                primary_sig = max(signals)
                signals.remove(primary_sig)

                # if there are signals other than primary
                if len(signals) > 0:
                    # calculate the noise
                    noise = np.log10(sum([10**(x/10) for x in signals]))*10
                    sir = primary_sig - noise
                else:
                    sir = max_sir_value

                # Record the sir
                SIR[grid_id] = {"sir": min(sir, max_sir_value), "coordinate": mysas.grids.get(grid_id)}

        # Record SIR for current channel
        Data[ch] = SIR

    # Find all CBSD coordinates
    cbsd_X = [cbsd.longitude for cbsd in mysas.CBSDs]
    cbsd_Y = [cbsd.latitude for cbsd in mysas.CBSDs]
    cbsd_C = [list(cbsd.channels) for cbsd in mysas.CBSDs]
    cbsd_cat = [cbsd.antenna_cat for cbsd in mysas.CBSDs]

    output = {"CBSDx": cbsd_X, "CBSDy": cbsd_Y, "CBSDc": cbsd_C, "CBSDcat": cbsd_cat, "heatmap": Data}
    return output


def get_plotdata_bw_interference(mysas, thresholds):
    """

    :type mysas: SAS
    :type thresholds: List[float]
    :return:
    """
    data = []
    bw0 = get_plotdata_bandwidth(mysas).get("avg_bw_actual")
    ix0 = get_plotdata_interference(mysas).get("overall_noises")
    et0 = "ETWF"

    data.append((ix0, bw0, et0))

    max_et_prac = max([cs.get("edge_threshold") for cs in mysas.CSs])

    for th in thresholds:
        if th >= max_et_prac:
            mysas.graph_coloring_all_at(th)
            if max([cs.get("chromatic") for cs in mysas.CSs]) <= channels_avail:
                mysas.assign_channels(partial_assign=False)
                bw = get_plotdata_bandwidth(mysas).get("avg_bw_actual")
                ix = get_plotdata_interference(mysas).get("overall_noises")
                et = "ET="+str(th)
                data.append((ix, bw, et))
    return data


def get_inter_cxg_ix(mysas):
    """

    :type mysas: SAS
    :return:
    """
    chs = range(1, channels_avail+1)
    cxg_ids = {cbsd.CxG for cbsd in mysas.CBSDs}
    inter_cxg_ixs = {}

    for cxg_id in cxg_ids:
        inter_cxg_ixs_ch = {}
        for ch in chs:
            # find all cbsd pairs for cbsds in this cxg with cbsds in other cxg using current channel
            cbsds_in_cxg = {cbsd for cbsd in mysas.CBSDs if cbsd.CxG == cxg_id and ch in cbsd.channels}
            cbsds_out_cxg = {cbsd for cbsd in mysas.CBSDs if cbsd.CxG != cxg_id and ch in cbsd.channels}
            pairs = [frozenset((x.id, y.id)) for x in cbsds_in_cxg for y in cbsds_out_cxg]

            # find the sum of the edge weights
            inter_cxg_ixs_ch[str(ch)] = sum(
                [mysas.ew_table.get(pair) for pair in set(pairs).intersection(mysas.ew_table.keys())]
            )
        inter_cxg_ixs[str(cxg_id)] = inter_cxg_ixs_ch

    return inter_cxg_ixs

def get_plotdata_origin_coverage(mysas):
    """
    Output Coverage map data for each cbsd

    Input:
            mysas:  SAS object
                :type mysas: SAS

    Return:
    """
    # Find all CBSDs' coverage
    Coverage = {}
    for cbsd in mysas.CBSDs:
        cvg = {key for key in cbsd.coverage.keys() if cbsd.coverage.get(key) >= min_rx}
        coordinate = [mysas.grids.get(key) for key in cvg]
        if len(coordinate) > 0:
            Ys, Xs = zip(*coordinate)
            Coverage[cbsd.id] = {"X": Xs, "Y": Ys, "color": list(cbsd.channels)}

    # Find all CBSD coordinates
    cbsd_X = [cbsd.longitude for cbsd in mysas.CBSDs]
    cbsd_Y = [cbsd.latitude for cbsd in mysas.CBSDs]
    cbsd_C = [list(cbsd.channels) for cbsd in mysas.CBSDs]
    cbsd_cat = [cbsd.antenna_cat for cbsd in mysas.CBSDs]

    output = {"CBSDx": cbsd_X, "CBSDy": cbsd_Y, "CBSDc": cbsd_C, "CBSDcat": cbsd_cat, "coverage": Coverage}

    return output


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


def txt_cdf(plotdatas, legends, text={}, outfile=""):
    """
    Plot CDF Figure given data_array and legends
    :type plotdatas:    List[float]
    :type legends:      List[String]
    :type text:         dict
    :type outfile:      str
    """
    content = "x\ty\tlegend\n"
    for plotdata, legend in zip(plotdatas, legends):
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

            # plt.plot(Xs, Ys, label=legend, c=colors[color_index/2], ls=linestyle, alpha=0.8)
            # plt.legend(loc=0)
            for val_x, val_y in zip(Xs, Ys):
                content += str(val_x) + "\t" + str(val_y) + "\t" + legend + "\n"
        # else:
        #     plt.scatter(0, 0, label=legend)

    f = open(outfile, "w")
    f.write(content)
    f.close()


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


def txt_bw_interfernce(datas, legends, text={}, outfile=""):
    content = "x\ty\tmarker\tlegend\n"

    for data, legend in zip(datas, legends):

        ixs, bws, ets = zip(*data)

        for val_ix, val_bw, val_et in zip(ixs, bws, ets):
            content += str(val_ix) + "\t" + str(val_bw) + "\t" + str(val_et) + "\t" + legend + "\n"

    f = open(outfile, "w")
    f.write(content)
    f.close()


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


def save_content(content, outfile):
    f = open(outfile, "w")
    json.dump(content, f)


def load_content(infile):
    f = open(infile)
    return json.load(f)





