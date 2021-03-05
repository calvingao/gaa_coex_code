import numpy as np
from gaa_sas import SAS
from gaa_cbsd import CBSD
import json
import ndpool as mp
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from adjustText import adjust_text


colors = ["blue", "orange", "green", "red", "purple", "brown", "pink", "olive", "yellow", "cyan"]     # Color Map
hatches = ['', 'O', '//', '*', '+', '-', 'o', '.', '*']
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


def get_inter_cxg_ix_cbsd((cbsd, mysas)):
    """
    Get Inter CxG AIPA Noise for each CBSD with best and worst channel

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
                                    if (other_cbsd.CxG != cbsd.CxG            # exclude same CxG
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


def get_plotdata_inter_cxg_ix_per_ch(mysas):
    """
    Output per channel inter_cxg interference Data of all CBSDs from given SAS

    Input:
            mysas:  SAS object
                :type mysas: SAS

    Return:
           sorted dbm_per_channel of each cbsd
    """
    avg_dbm_per_ch = [get_per_unit_dbm([get_inter_cxg_ix_cbsd((cbsd, mysas))[2]],
                                       len(cbsd.channels) * len({key for key in cbsd.coverage.keys()
                                                                 if cbsd.coverage.get(key) >= min_rx
                                                                 })
                                       )
                      for cbsd in mysas.CBSDs]

    avg_dbm_per_ch.sort()
    avg_ix_per_ch_per_cbsd = get_per_unit_dbm(avg_dbm_per_ch, float(len(mysas.CBSDs)))

    maxmin = get_plotdata_inter_cxg_interference(mysas)

    return {"dbm_per_ch": avg_dbm_per_ch,
            "avg_ix_per_ch_per_cbsd": avg_ix_per_ch_per_cbsd,
            "max_noises": maxmin.get("max_noises"),
            "min_noises": maxmin.get("min_noises")}


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

def get_plotdata_inter_cxg_interference(mysas):
    """
    Output InterCxG Interference data of all CBSDs from given SAS

    Input:
            mysas:  SAS object
                :type mysas: SAS

    Return:
            CDF Plot Data for interference
    """
    cbsd_noises_max = {}
    cbsd_noises_min = {}

    ret = [get_inter_cxg_ix_cbsd((cbsd, mysas)) for cbsd in mysas.CBSDs]

    maxns, minns, accumulated_noises = zip(*ret)

    for cbsd, max_noise, min_noise in zip(mysas.CBSDs, maxns, minns):
        cbsd_noises_max[cbsd] = max_noise
        cbsd_noises_min[cbsd] = min_noise

    max_noises = cbsd_noises_max.values()
    max_noises.sort()
    min_noises = cbsd_noises_min.values()
    min_noises.sort()

    result = {"max_noises": max_noises, "min_noises": min_noises}
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


def get_inter_cxg_ix_app3(mysas, et):
    """

    :type mysas: SAS
    :type et: float
    :return:
    """

    # Find all CBSDs with the potential edge neighbors
    potential_pairs = mysas.get_approach_3(et)

    # Create dict for potential inter-cxg noise of each CBSD
    noises = {}

    for each_cbsd in mysas.CBSDs:
        # Find its coverage area in grids
        covered_grids = {key for key in each_cbsd.coverage.keys() if each_cbsd.coverage.get(key) >= min_rx}

        interference_in_coverage = []
        for grid in covered_grids:
            interference_in_grid = [other_cbsd.coverage.get(grid) for other_cbsd in mysas.CBSDs
                                    if (other_cbsd.id in potential_pairs.get(each_cbsd.id)[1]  # from the potential edge
                                        and other_cbsd.coverage.get(grid) >= min_rx)  # Above Threshold
                                    ]

            # Update list of each interference
            if len(interference_in_grid) > 0:
                interference_in_coverage.extend(interference_in_grid)

        # if there are interferences over min_rx (-96dbm by default), calculate effective interferences
        # otherwise set noise to None
        noises[each_cbsd.id] = get_per_unit_dbm(interference_in_coverage, len(covered_grids)) \
            if len(interference_in_coverage) > 0 else None

    return noises

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


def plot_cdf(plotdatas, legends, styles, text={}, outfile=""):
    """
    Plot CDF Figure given data_array and legends
    :type plotdatas:    List[float]
    :type legends:      List[String]
    :type styles:      List[tuple]
    :type text:         dict
    :type outfile:      str
    """
    for plotdata, legend, style in zip(plotdatas, legends, styles):
        linestyle = style[0]
        color_index = style[1]

        # Count Number of Nones
        Num_None = [v for v in plotdata if v is None].count(None)
        # x-value for all non-None value
        if Num_None != len(plotdata):
            Xs = [v for v in plotdata if v is not None]
            Xs.insert(0, Xs[0])
            Xs.append(text.get("xlim")[1])
            # percentage of total numbers
            Ys = [index/float(len(plotdata))*100 for index in range(Num_None+1, len(plotdata)+1)]
            Ys.insert(0, 0)
            Ys.append(Ys[-1])

            plt.plot(Xs, Ys, label=legend, c=colors[color_index % len(colors)], ls=linestyle, alpha=0.8)
            plt.legend(loc=0)
        else:
            plt.scatter(0, 0, label=legend)

    if text.get("title") is not None:
        plt.title(text.get("title"))
    plt.xlabel(text.get("xlabel"))
    plt.ylabel(text.get("ylabel"))
    plt.xlim(text.get("xlim"))
    plt.ylim(text.get("ylim"))
    plt.legend(loc=0, fontsize=8, ncol=1)
    # plt.show()
    plt.savefig(outfile)
    plt.close()


def plot_bar(plotdatas, legends, stacks=[], text={}, outfile=""):
    """
    Plot CDF Figure given data_array and legends
    :type plotdatas:    List[dict]
    :type legends:      List[String]
    :type stacks:      List
    :type text:         dict
    :type outfile:      str
    """
    stackbars=[]
    for item in stacks:
        stackbars.append([])

    r = range(len(plotdatas))
    bar_width = 0.5
    grid_width = 1.0
    r = [i * grid_width - 0.5 for i in r]

    for plotdata in plotdatas:
        for key in stacks:
            if key in plotdata.keys():
                stackbars[stacks.index(key)].append(plotdata.get(key) * 100)
            else:
                stackbars[stacks.index(key)].append(0.0)

    fig = plt.figure()

    bottoms = [0] * len(legends)
    for stack in stacks:
        index_stack = stacks.index(stack)
        plt.bar(r, stackbars[index_stack], bottom=bottoms, color=colors[index_stack],
                label=stacks[index_stack]+" MHz", edgecolor='white', width=bar_width, align='center')
        bottoms = [i+j for i, j in zip(bottoms, stackbars[index_stack])]

    if text.get("title") is not None:
        plt.title("Histogram of Bandwidth: " + text.get("title"))
    plt.xticks(r, legends, rotation=45)
    plt.xlabel(text.get("xlabel"))
    plt.ylabel(text.get("ylabel"))
    plt.ylim(0, 110)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=4, fontsize=12)
    fig.subplots_adjust(bottom=0.2)

    # plt.show()
    plt.savefig(outfile)
    plt.close()

def plot_histo(plotdatas, legends, stacks=[], text={}, outfile=""):
    """
    Plot CDF Figure given data_array and legends
    :type plotdatas:    List[dict]
    :type legends:      List[String]
    :type stacks:      List
    :type text:         dict
    :type outfile:      str
    """
    stackbars = []
    for item in plotdatas:
        stackbars.append([])

    r = range(len(stacks))
    bar_width = 0.1
    # grid_width = 1.0
    # r = [i * grid_width - 0.5 for i in r]

    for stackbar, plotdata in zip(stackbars, plotdatas):
        for key in stacks:
            if key in plotdata.keys():
                stackbar.append(plotdata.get(key) * 100)
            else:
                stackbar.append(0.0)

    fig = plt.figure()
    ax = plt.subplot(111)
    for stackbar, legend in zip(stackbars, legends):
        index_legend = legends.index(legend)
        ax.bar([i+(0.1 * (index_legend-3.5)) for i in r], stackbar, color=colors[index_legend/4],
                label=legend + " MHz", edgecolor='white', hatch=hatches[index_legend%4], width=bar_width, align='center')

    if text.get("title") is not None:
        plt.title("Histogram of Bandwidth: " + text.get("title"))
    plt.xticks(r, stacks, rotation=45)
    plt.xlabel("Assigned Bandwidth (MHz)")
    plt.ylabel(text.get("ylabel"))
    # plt.ylim(0, 110)
    plt.legend(loc=9, ncol=1, fontsize=10)
    fig.subplots_adjust(bottom=0.15)

    # plt.show()
    plt.savefig(outfile)
    plt.close()

def plot_bw_interfernce(datas, legends, styles, text={}, outfile=""):
    max_ix = text.get("xlim")[0]
    min_ix = text.get("xlim")[1]

    for data in datas:
        ixs, bws, ets = zip(*data)

        de_none_ixs = [x for x in ixs if x is not None]
        if len(de_none_ixs)>0:
            max_ix = max(max(de_none_ixs), max_ix)
            min_ix = min(min(de_none_ixs), min_ix)

    texts = []

    for data, legend, style in zip(datas, legends, styles):
        linestyle = style[0]
        marker = "s" if linestyle == "solid" else "o"
        color_index = style[1]

        ixs, bws, ets = zip(*data)

        revert_ixs = []
        for ix in ixs:
            if ix is None:
                revert_ixs.append(min_ix)
            else:
                revert_ixs.append(ix)
        ixs = revert_ixs

        plt.scatter(ixs, bws, c=colors[color_index], marker=marker, alpha=0.8)
        plt.plot(ixs, bws, c=colors[color_index], label=legend, ls=linestyle)

        # for ix, bw, et in zip(ixs, bws, ets):
        #     # plt.annotate(et, (ix, bw), textcoords="offset points", xytext=(3, -8), fontsize=8, ha='left')
        #     texts.append(plt.text(ix, bw, et, fontsize=8))

    if text.get("title") is not None:
        plt.title(text.get("title"))
    plt.xlabel(text.get("xlabel"))
    plt.ylabel(text.get("ylabel"))
    # plt.xlim(float(int(min_ix/10)*10-10), float(int(max_ix/10)*10))
    plt.xlim(-110, -30)
    plt.ylim(text.get("ylim"))
    plt.legend(loc=0, fontsize=12)

    # adjust_text(texts, arrowprops=dict(arrowstyle="->", color='r', lw=0.5))

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


def save_content(content, outfile):
    f = open(outfile, "w")
    json.dump(content, f)


def load_content(infile):
    f = open(infile)
    return json.load(f)


def get_bw_app3(mysas, et):
    """
    Output Maximum possible Bandwidth Assignment to each CBSD from given SAS using Approach 3

    Input:
            mysas:  SAS object
                :type mysas: SAS
            et:     edge threshold value
                :type et: float

    Return:
           et, bw_max_cdf
    """
    # Total Bandwidth
    Total_BandWidth = len(mysas.channels) * 10.0

    # Max Bandwidth Assigned to each CBSD
    assignment = mysas.get_approach_3(et)
    bw_max_per_cbsd = {key: Total_BandWidth/val[0] for key, val in assignment.items()}

    bw_max_cdf = bw_max_per_cbsd.values()
    bw_max_cdf.sort()

    avg_bw_max = np.mean(bw_max_cdf)

    ret = {"et": et,
           "cdf_bw_max": bw_max_cdf,
           "avg_bw_max": avg_bw_max
           }

    return ret


def get_ix_app3(mysas, et):
    """
    Output Potential Interference in form of Accumulated EW to each CBSD from given SAS using Approach 3

    Input:
            mysas:  SAS object
                :type mysas: SAS
            et:     edge threshold value
                :type et: float

    Return:
           et, ix_cdf
    """
    # interference from outside CxG to each CBSD
    assignment = get_inter_cxg_ix_app3(mysas, et)
    ix_per_cbsd = {key: val for key, val in assignment.items()}

    ix_max_cdf = ix_per_cbsd.values()
    ix_max_cdf.sort()

    avg_ix_max = get_per_unit_dbm(ix_max_cdf, float(len(mysas.CBSDs)))

    ret = {"et": et,
           "cdf_ix": ix_max_cdf,
           "avg_ix_max": avg_ix_max
           }

    return ret


def plot_group_cdf(group, text={}, outfile=""):
    ncol = len(group)
    nrow = len(group[0]) if ncol > 0 else 0

    fig, axs = plt.subplots(nrow, ncol, sharex=True, sharey=True)
    for col in range(ncol):
        for row in range(nrow):
            ax = axs[row, col]
            plotdatas = group[col][row][0]
            legends = group[col][row][1]
            styles = group[col][row][2]
            grp_txt = group[col][row][3]
            print grp_txt

            for plotdata, legend, style in zip(plotdatas, legends, styles):
                linestyle = style[0]
                color_index = style[1]

             # Count Number of Nones
                Num_None = [v for v in plotdata if v is None].count(None)
                # x-value for all non-None value
                if Num_None != len(plotdata):
                    Xs = [v for v in plotdata if v is not None]
                    Xs.insert(0, Xs[0])
                    Xs.append(text.get("xlim")[1])
                    # percentage of total numbers
                    Ys = [index/float(len(plotdata))*100 for index in range(Num_None+1, len(plotdata)+1)]
                    Ys.insert(0, 0)
                    Ys.append(Ys[-1])

                    ax.plot(Xs, Ys, label=legend, c=colors[color_index % len(colors)], ls=linestyle, alpha=0.8)
                else:
                    ax.scatter(0, 0, label=legend)
            ax.title.set_text(grp_txt)

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", fontsize=8, bbox_to_anchor=(0.5, 0), ncol=4)
    fig.subplots_adjust(bottom=0.2)

    fig.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axes
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)
    plt.xlabel(text.get("xlabel"))
    plt.ylabel(text.get("ylabel"))

    plt.xlim(text.get("xlim"))
    plt.ylim(text.get("ylim"))
    # plt.show()
    plt.savefig(outfile)
    plt.close()


def plot_group_histo(group, stacks=[], text={}, outfile=""):
    ncol = len(group)
    nrow = len(group[0]) if ncol > 0 else 0

    r = range(len(stacks))
    bar_width = 0.05

    fig, axs = plt.subplots(nrow, ncol, sharex=True, sharey=True)
    for col in range(ncol):
        for row in range(nrow):
            ax = axs[row, col]
            plotdatas = group[col][row][0]
            legends = group[col][row][1]
            styles = group[col][row][2]
            grp_txt = group[col][row][3]
            print grp_txt

            stackbars = []
            for item in plotdatas:
                stackbars.append([])


            for stackbar, plotdata in zip(stackbars, plotdatas):
                for key in stacks:
                    if key in plotdata.keys():
                        stackbar.append(plotdata.get(key) * 100)
                    else:
                        stackbar.append(0.0)

            for stackbar, legend, style in zip(stackbars, legends, styles):
                index_legend = legends.index(legend)
                linestyle = style[0]
                color_index = style[1]
                ax.bar([i + (0.07 * (index_legend - 6)) for i in r], stackbar, color=colors[color_index],
                       label=legend + " MHz", edgecolor='white', hatch=hatches[linestyle], width=bar_width,
                       align='center')

            ax.title.set_text(grp_txt)
            plt.xlim((0, 5))
            plt.xticks(r, stacks)



    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", fontsize=8, bbox_to_anchor=(0.5, 0), ncol=4)
    fig.subplots_adjust(bottom=0.2)

    fig.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axes
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)
    plt.xlabel("Assigned Bandwidth (MHz)")
    plt.ylabel(text.get("ylabel"))
    plt.ylim(text.get("ylim"))
    # plt.show()
    plt.savefig(outfile)
    plt.close()


def plot_group(group, text={}, outfile=""):
    ncol = len(group)
    nrow = len(group[0]) if ncol > 0 else 0

    fig, axs = plt.subplots(nrow, ncol, sharex=False, sharey=False, figsize=text.get("figsize"))

    fig.tight_layout(rect=[0.05, 0, 1, 0.95])
    for col in range(ncol):
        for row in range(nrow):
            ax = axs[row, col]
            plotdatas = group[col][row][0]
            legends = group[col][row][1]
            styles = group[col][row][2]
            grp_txt = group[col][row][3]
            print grp_txt

            for plotdata, legend, style in zip(plotdatas, legends, styles):
                linestyle = style[0]
                color_index = style[1]

                marker = "s" if linestyle == "solid" else "o"

                Xs, Ys = zip(*plotdata)

                ax.scatter(Xs, Ys, c=colors[color_index % len(colors)], marker=marker, alpha=0.8)
                ax.plot(Xs, Ys, c=colors[color_index % len(colors)], label=legend, ls=linestyle)
            ax.title.set_text(grp_txt)

            ax.set_xlim(text.get("xlim"))
            ax.set_ylim(text.get("ylim"))

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", fontsize=10, bbox_to_anchor=(0.5, 0), ncol=len(plotdatas))
    fig.subplots_adjust(bottom=0.1)

    fig.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axes
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)
    plt.xlabel(text.get("xlabel"))
    plt.ylabel(text.get("ylabel"))

    # plt.show()
    plt.savefig(outfile)
    plt.close()
