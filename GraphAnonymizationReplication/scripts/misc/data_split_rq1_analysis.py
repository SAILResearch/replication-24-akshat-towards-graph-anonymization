import os

import pandas as pd
import matplotlib.pyplot as plt
# import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import numpy as np


# from adjustText import adjust_text


def get_label(__att):
    if __att == "privacy_measure_found_percentage":
        label = "Privacy Found Percentage"
    elif __att == "privacy_measure_tim_ipr":
        label = "Privacy IPR"
    elif __att == "privacy_measure_my_ipr_metric":
        label = "Privacy_My_IPR"
    elif __att == "rf_results_auc":
        label = "AUC"
    elif __att == "rf_results_rec":
        label = "Recall"
    elif __att == "rf_results_pre":
        label = "Precision"
    elif __att == "graph_privacy_tim_ipr":
        label = "Graph_Privacy_IPR"
    elif __att == "graph_privacy_found_percentage":
        label = "Graph_Privacy_Found_Percentage"
    else:
        raise ValueError("Unknown attribute")

    return label


if __name__ == "__main__":

    p_l_1 = 40
    p_l_2 = 65
    p_l_3 = 80

    fontsize_privacy = 18
    line_width = 3

    rq = "data_split_rq1"
    os.makedirs(f"stat_test/{rq}", exist_ok=True)

    clean_result_dir = "../../final_data/rq2"

    dataset_list = ["openstack", "apache_flink", "apache_ignite", "apache_cassandra", "qt", "apache_groovy"]
    technique_name = ["random_add_delete", "random_switch", "k_da_anon", "gen"]
    combined_df = pd.DataFrame()

    sns.set_style("white")

    for __d in dataset_list:

        file_list = []

        for __cf in os.listdir(clean_result_dir):
            if __d in __cf and "final" in __cf and "~$" not in __cf and "clean" in __cf:
                file_list.append(os.path.join(clean_result_dir, __cf))

        if len(file_list) == 0:
            print("Error: cannot find file for technique {}".format(__d))
            continue

        print("Processing data {}...".format(__d))

        # # sns.set_theme(style="darkgrid")
        sns.set_style("white")
        plt.figure(figsize=(15, 8))
        plt.ylim(0, 1)

        minx = 1
        maxx = 0

        miny = 1
        maxy = 0

        baseline_auc = None

        # increase font size

        for __p in ["privacy_measure_tim_ipr", "privacy_measure_found_percentage"]:

            # plt.clf()
            plt.figure(figsize=(15, 8))
            plt.rcParams['legend.fontsize'] = fontsize_privacy
            plt.rcParams['legend.title_fontsize'] = fontsize_privacy
            plt.rcParams['axes.labelsize'] = fontsize_privacy
            plt.rcParams['axes.titlesize'] = fontsize_privacy
            plt.rcParams['xtick.labelsize'] = fontsize_privacy
            plt.rcParams['ytick.labelsize'] = fontsize_privacy

            print("Processing privacy measure {}...".format(__p))

            for __file in file_list:

                clean_df = pd.read_excel(__file)
                file_name = os.path.basename(__file).replace("data_split_", "").replace("_train", "")
                file_name = \
                    os.path.basename(file_name).replace("final_", "").replace(__d + "_", "").replace("_results",
                                                                                                     "").replace(
                        "_clean.xlsx", "").split(" ")[0]

                print("File name: {}".format(file_name))

                if  file_name == "camel":
                    continue

                clean_df[__p] = clean_df[__p].apply(float)
                clean_df[__p] = clean_df[__p] * 100

                # clean_df["privacy_average"] = clean_df.apply(
                #     lambda x: round((x["privacy_measure_tim_ipr"] + x["privacy_measure_found_percentage"]) / 2, 4), axis=1)
                clean_df["links_changed"] = clean_df["joined_key"].apply(lambda x: x.split("_")[2])
                clean_df["iteration"] = clean_df["joined_key"].apply(lambda x: x.split("_")[0])
                # assign each row a number
                clean_df["row_number"] = clean_df.index

                print("File name: {}".format(file_name))
                clean_df["iteration"] = clean_df["iteration"].apply(int)
                size = clean_df["iteration"].max()
                # if baseline_auc is None:
                #     baseline_auc = clean_df[clean_df["iteration"] == "-1"]["rf_results_auc"].values[0]

                # remove 0 links changed
                clean_df = clean_df[clean_df["links_changed"] != "0"]
                clean_df = clean_df[clean_df["links_changed"] != "nan"]
                # clean_df["links_changed"] = clean_df["links_changed"].astype(float)

                # xaxis = "privacy_average"
                # yaxis = "rf_results_auc"

                # if clean_df[yaxis].min() < miny:
                #     miny = clean_df[yaxis].min()
                # if clean_df[yaxis].max() > maxy:
                #     maxy = clean_df[yaxis].max()
                #
                # if clean_df[xaxis].min() < minx:
                #     minx = clean_df[xaxis].min()
                # if clean_df[xaxis].max() > maxx:
                #     maxx = clean_df[xaxis].max()

                # color

                if "random_add_delete" in file_name:
                    color = "red"
                elif "random_switch" in file_name:
                    color = "blue"
                elif "gen" in file_name:
                    color = "green"
                elif "k_da" in file_name:
                    color = "orange"

                clean_df["diff"] = clean_df[__p].diff()
                clean_df["x_diff"] = clean_df.apply(lambda x: x["row_number"] - 0.5, axis=1)

                clean_df["y_diff"] = clean_df.apply(lambda x: x[__p] - x["diff"] / 2, axis=1)

                cumulative_gain_name = f"{file_name}_{__d}_{__p}"
                print(f"Technique: {file_name} - {__d} - {__p}")

                if __d == "qt":
                    print("QT")

                # for column __p find the cumulative change and normalize it
                max_value = clean_df[__p].max()
                # clean_df[f"{__p}_cumulative_gain"] = clean_df[__p].apply(lambda __x: max_value - __x)
                # clean_df[f"{__p}_cumulative_gain"] = clean_df[f"{__p}_cumulative_gain"].apply(
                #     lambda __x: max_value - __x)
                # clean_df[f"{__p}_cumulative_gain"] = clean_df[f"{__p}_cumulative_gain"] / max_value
                # clean_df[f"{__p}_cumulative_gain"] = clean_df[f"{__p}_cumulative_gain"] * 100
                # clean_df[f"{__p}_cumulative_gain"] = clean_df[f"{__p}_cumulative_gain"].round(2)
                # clean_df[f"{__p}_cumulative_gain"] = clean_df[f"{__p}_cumulative_gain"].astype(str)
                # clean_df[f"{__p}_cumulative_gain"] = clean_df.apply(
                #     lambda __x: __x[f"{__p}_cumulative_gain"] + " - " + str(__x["iteration"]), axis=1)
                # # clean_df[f"{__p}_cumulative_gain"] = clean_df[f"{__p}_cumulative_gain"].cumsum()
                # # print(clean_df[f"{__p}_cumulative_gain"])
                #
                # combined_df[cumulative_gain_name] = clean_df[f"{__p}_cumulative_gain"]
                file_name = file_name.title()

                sns.lineplot(x="row_number", y=__p, data=clean_df, markers=True, dashes=False,
                             label=file_name, marker='o', color=color, linewidth=line_width)
                for x, y, z, diff, x_diff, y_diff in zip(clean_df["row_number"], clean_df[__p], clean_df["iteration"],
                                                         clean_df["diff"], clean_df["x_diff"], clean_df["y_diff"]):
                    delta = 4
                    if __p == "privacy_measure_tim_ipr":
                        if __d == "openstack":
                            if "k_da" in file_name:
                                delta = 0
                        if __d == "apache_flink":
                            if "gen" in file_name:
                                delta = -2
                            if "k_da" in file_name and x in [1, 2]:
                                delta = -2

                    # if abs(round(diff, 2)) > 1:
                    #     plt.text(x_diff, y_diff, f'{diff:.0f}', ha='center', va='bottom', fontsize=10, rotation=45,
                    #              color=color)

                    # plt.text(x, y - delta - 2, f'{z}', ha='center', va='bottom', fontsize=fontsize_privacy, rotation=45)

            # plt.plt

            # plt.text(18, p_l_1, "Privacy Level I", ha='center', va='bottom', fontsize=fontsize_privacy, rotation=0)
            plt.plot([0, 19], [p_l_2, p_l_2], color='black', linestyle='dotted', linewidth=line_width)
            plt.text(18, p_l_2, "Privacy Level I", ha='center', va='bottom', fontsize=fontsize_privacy, rotation=0)
            plt.plot([0, 19], [p_l_3, p_l_3], color='black', linestyle='dotted', linewidth=line_width)
            plt.text(18, p_l_3, "Privacy Level II", ha='center', va='bottom', fontsize=fontsize_privacy, rotation=0)

            plt.plot([0, 19], [100, 100], color='red', linestyle='--', linewidth=line_width)
            plt.xticks(range(0, 19, 1))
            plt.title(f"{__d}")
            plt.ylim(0, 105)
            plt.yticks(np.arange(0, 105, 10))
            plt.xlabel("Configuration Level")
            plt.ylabel(get_label(__p))
            plt.legend()
            # increase the legend font size by 10

            # print(plt.rcParams.keys())
            plt.rcParams['legend.fontsize'] = fontsize_privacy
            plt.rcParams['legend.title_fontsize'] = fontsize_privacy
            plt.rcParams['axes.labelsize'] = fontsize_privacy
            plt.rcParams['axes.titlesize'] = fontsize_privacy
            plt.rcParams['xtick.labelsize'] = fontsize_privacy
            plt.rcParams['ytick.labelsize'] = fontsize_privacy

            # plt.rcParams.update({'font.size': 30})
            plt.savefig(f"stat_test/{rq}/{rq}_{__d}_{__p}.png", format="png")
            plt.close()
        # plt.show()

    # combined_df.to_excel(f"stat_test/{rq}/{rq}_combined.xlsx", index=False)

    for __t in technique_name:

        file_list = []

        for __cf in os.listdir(clean_result_dir):
            if __t in __cf and "final" in __cf and "~$" not in __cf and "clean" in __cf:
                file_list.append(os.path.join(clean_result_dir, __cf))

        if len(file_list) == 0:
            print("Error: cannot find file for technique {}".format(__t))
            continue

        print("Processing data {}...".format(__t))

        size = 0
        for __p in ["privacy_measure_tim_ipr", "privacy_measure_found_percentage"]:
            plt.clf()

            sns.set_theme(style="darkgrid")
            # sns.set_style("whitegrid")
            plt.figure(figsize=(15, 8))
            plt.ylim(0, 1)

            plt.rcParams['legend.fontsize'] = fontsize_privacy
            plt.rcParams['legend.title_fontsize'] = fontsize_privacy
            plt.rcParams['axes.labelsize'] = fontsize_privacy
            plt.rcParams['axes.titlesize'] = fontsize_privacy
            plt.rcParams['xtick.labelsize'] = fontsize_privacy
            plt.rcParams['ytick.labelsize'] = fontsize_privacy

            print("Processing privacy measure {}...".format(__p))

            minx, maxx = 0, 0
            miny, maxy = 0, 0

            for __file in file_list:

                # clean_df = pd.read_excel(__file)
                # file_name = \
                #     os.path.basename(__file).replace("final_", "").replace(__t + "_", "").replace("_results", "").replace(
                #         "_clean.xlsx", "").split(" ")[0]

                file_name = os.path.basename(__file).replace("data_split_", "").replace("_train", "")
                __temp_file_name = os.path.basename(file_name).split("_")[0]
                if __temp_file_name == "apache":
                    __temp_file_name = os.path.basename(file_name).split("_")[1]
                file_name = __temp_file_name
                clean_df = pd.read_excel(__file)
                if file_name == "camel":
                    continue

                clean_df[__p] = clean_df[__p].astype(float)
                clean_df[__p] = clean_df[__p] * 100

                # clean_df["privacy_average"] = clean_df.apply(
                #     lambda x: round((x["privacy_measure_tim_ipr"] + x["privacy_measure_found_percentage"]) / 2, 4),
                #     axis=1)
                clean_df["links_changed"] = clean_df["joined_key"].apply(lambda x: x.split("_")[2])
                clean_df["iteration"] = clean_df["joined_key"].apply(lambda x: x.split("_")[0])
                # assign each row a number
                clean_df["row_number"] = clean_df.index

                print("File name: {}".format(file_name))

                xaxis = "iteration"
                clean_df[xaxis] = clean_df[xaxis].astype(float)
                size = clean_df[xaxis].max()

                # size = len /(clean_df)

                # if baseline_auc is None:
                #     baseline_auc = clean_df[clean_df["iteration"] == "-1"]["rf_results_auc"].values[0]

                # remove 0 links changed
                clean_df = clean_df[clean_df["links_changed"] != "0"]
                clean_df = clean_df[clean_df["links_changed"] != "nan"]
                # clean_df["links_changed"] = clean_df["links_changed"].astype(float)

                # xaxis = "privacy_average"
                # yaxis = "rf_results_auc"

                # if clean_df[yaxis].min() < miny:
                #     miny = clean_df[yaxis].min()
                # if clean_df[yaxis].max() > maxy:
                #     maxy = clean_df[yaxis].max()
                #
                if clean_df[xaxis].min() < minx:
                    minx = clean_df[xaxis].min()
                if clean_df[xaxis].max() > maxx:
                    maxx = clean_df[xaxis].max()

                # color

                if "random_add_delete" in file_name or "openstack" in file_name:
                    color = "red"
                elif "random_switch" in file_name or "flink" in file_name:
                    color = "blue"
                elif "gen" in file_name or "ignite" in file_name:
                    color = "green"
                elif "k_da" in file_name or "cassandra" in file_name:
                    color = "orange"
                elif "groovy" in file_name:
                    color = "purple"
                elif "qt" in file_name:
                    color = "pink"

                clean_df["diff"] = clean_df[__p].diff()
                xxdiff_delta = 0.9
                if __t == "gen":
                    xxdiff_delta = 0.98
                clean_df["x_diff"] = clean_df.apply(lambda x: x[xaxis] * xxdiff_delta, axis=1)
                clean_df["y_diff"] = clean_df.apply(lambda x: x[__p] * 1.001, axis=1)
                file_name = file_name.title()

                sns.lineplot(x=xaxis, y=__p, data=clean_df, markers=True, dashes=False,
                             label=file_name, marker='o', color=color, linewidth=line_width)
                for x, y, z, diff, x_diff, y_diff in zip(clean_df[xaxis], clean_df[__p], clean_df["iteration"],
                                                         clean_df["diff"], clean_df["x_diff"], clean_df["y_diff"]):
                    delta = 4
                    if __p == "privacy_measure_tim_ipr":
                        if file_name == "openstack":
                            if "k_da" in file_name:
                                delta = 0.00
                        if file_name == "apache_flink":
                            if "gen" in file_name:
                                delta = -2
                            if "k_da" in file_name and x in [1, 2]:
                                delta = -2

                    # if abs(round(diff, 2)) > 1:
                    #     plt.text(x_diff, y_diff, f'{diff:.0f}', ha='center', va='bottom', fontsize=10, rotation=45,
                    #              color=color)

                    # plt.text(x, y - delta, f'{z}', ha='center', va='bottom', fontsize=10, rotation=45)
                    # if x == 0 or x == size - 1:
                    #     plt.text(x, y + delta, f'{y:.2f}', ha='center', va='bottom', fontsize=10, rotation=45)

            plt.plot([0, size], [100, 100], color='red', linestyle='dotted', linewidth=line_width)
            # plt.xticks(range(0, size, 1))

            if __t == "random_add_delete":
                title = "Random Add/Delete"
                xticks = np.arange(0, 104, 10)
                xlim = 0, 104
                start = 96
            elif __t == "random_switch":
                title = "Random Switch"
                xticks = np.arange(0, 104, 10)
                xlim = 0, 104
                start = 96
            elif __t == "k_da_anon":
                title = "K-DA"
                xticks = np.arange(1, 25, 1)
                xlim = 1, 25
                start = 24
            elif __t == "gen":
                title = "Generalisation"
                xticks = np.arange(0, 120, 10)
                xlim = 0, 120
                start = 110


            # plt.text(start, p_l_1, "Privacy Level I", ha='center', va='bottom', fontsize=fontsize_privacy, rotation=0)
            plt.plot([0, size], [p_l_2, p_l_2], color='black', linestyle='dotted', linewidth=line_width)
            plt.text(start, p_l_2, "Privacy Level I", ha='center', va='bottom', fontsize=fontsize_privacy, rotation=0)
            plt.plot([0, size], [p_l_3, p_l_3], color='black', linestyle='dotted', linewidth=line_width)
            plt.text(start, p_l_3, "Privacy Level II", ha='center', va='bottom', fontsize=fontsize_privacy, rotation=0)

            # print(plt.rcParams.keys())

            plt.title(f"{title}")
            plt.ylim(0, 105)
            plt.yticks(np.arange(0, 105, 10), fontsize=fontsize_privacy)

            # xxdelta = (maxx - minx)/20
            # plt.xlim(minx - xxdelta, maxx + xxdelta)
            # plt.xticks(np.arange(minx, maxx+xxdelta*2, xxdelta))
            # plt.xticks(clean_df[xaxis].values)

            plt.xlim(xlim)
            plt.xticks(xticks, fontsize=fontsize_privacy)

            plt.xlabel("Configuration Level", fontsize=fontsize_privacy)
            plt.ylabel(get_label(__p), fontsize=fontsize_privacy)
            # place legend at bottom right
            plt.legend(loc='lower right', fontsize=fontsize_privacy)
            # plt.legend()

            plt.rcParams['legend.fontsize'] = fontsize_privacy
            plt.rcParams['legend.title_fontsize'] = fontsize_privacy
            plt.rcParams['axes.labelsize'] = fontsize_privacy
            plt.rcParams['axes.titlesize'] = fontsize_privacy
            plt.rcParams['xtick.labelsize'] = fontsize_privacy
            plt.rcParams['ytick.labelsize'] = fontsize_privacy

            # plt.rcParams.update({'font.size': 30})
            plt.savefig(f"stat_test/{rq}/{rq}_{__t}_{__p}.png", format="png")
            plt.close('all')
            # plt.show()

    # plt.close('all')
    for __t in dataset_list:

        file_list = []

        for __cf in os.listdir(clean_result_dir):
            if __t in __cf and "final" in __cf and "~$" not in __cf and "clean" in __cf:
                file_list.append(os.path.join(clean_result_dir, __cf))

        if len(file_list) == 0:
            print("Error: cannot find file for technique {}".format(__t))
            continue

        print("Processing data {}...".format(__t))

        for __p in ["privacy_measure_tim_ipr", "privacy_measure_found_percentage", "rf_results_auc", "rf_results_rec"]:
            plt.clf()

            minx, maxx = 0, 0
            miny, maxy = 0, 0

            # # sns.set_theme(style="darkgrid")
            # sns.set_style("whitegrid")
            plt.figure(figsize=(15, 8))
            plt.rcParams['legend.fontsize'] = fontsize_privacy
            plt.rcParams['legend.title_fontsize'] = fontsize_privacy
            plt.rcParams['axes.labelsize'] = fontsize_privacy
            plt.rcParams['axes.titlesize'] = fontsize_privacy
            plt.rcParams['xtick.labelsize'] = fontsize_privacy
            plt.rcParams['ytick.labelsize'] = fontsize_privacy

            print("Processing privacy measure {}...".format(__p))

            size = 0
            baseline_performance = 0

            for __file in file_list:

                # clean_df = pd.read_excel(__file)
                # file_name = \
                #     os.path.basename(__file).replace("final_", "").replace(__t + "_", "").replace("_results", "")
                #     .replace(
                #         "_clean.xlsx", "").split(" ")[0]
                clean_df = pd.read_excel(__file)
                file_name = os.path.basename(__file).replace("data_split_", "").replace("_train", "")
                file_name = \
                    os.path.basename(file_name).replace("final_", "").replace(__t + "_", "").replace("_results",
                                                                                                  "").replace(
                        "_clean.xlsx", "").split(" ")[0]

                if file_name == "camel":
                    continue

                clean_df[__p] = clean_df[__p].astype(float)
                clean_df[__p] = clean_df[__p] * 100

                clean_df["links_changed"] = clean_df["joined_key"].apply(lambda x: x.split("_")[2])
                clean_df["nodes_changed"] = clean_df["joined_key"].apply(lambda x: x.split("_")[1])
                clean_df["iteration"] = clean_df["joined_key"].apply(lambda x: x.split("_")[0])
                # assign each row a number
                clean_df["row_number"] = clean_df.index

                print("File name: {}".format(file_name))

                if __p in ["rf_results_auc", "rf_results_rec"]:
                    baseline_performance = clean_df[clean_df["iteration"] == "-1"][__p].values[0]

                # if baseline_auc is None:
                #     baseline_auc = clean_df[clean_df["iteration"] == "-1"]["rf_results_auc"].values[0]

                # remove 0 links changed
                clean_df = clean_df[clean_df["links_changed"] != "0"]
                clean_df = clean_df[clean_df["links_changed"] != "nan"]
                clean_df["links_changed"] = clean_df["links_changed"].astype(float)
                clean_df["nodes_changed"] = clean_df["nodes_changed"].astype(float)

                xaxis = "links_changed"
                yaxis = __p

                if clean_df[yaxis].min() < miny:
                    miny = clean_df[yaxis].min()
                if clean_df[yaxis].max() > maxy:
                    maxy = clean_df[yaxis].max()

                if clean_df[xaxis].min() < minx:
                    minx = clean_df[xaxis].min()
                if clean_df[xaxis].max() > maxx:
                    maxx = clean_df[xaxis].max()

                # color

                if "random_add_delete" in file_name:
                    color = "red"
                elif "random_switch" in file_name:
                    color = "blue"
                elif "gen" in file_name:
                    color = "green"
                elif "k_da" in file_name:
                    color = "orange"

                if file_name == "random_add_delete":
                    title = "Random Add/Delete"
                    # xticks = np.arange(0, 104, 10)
                    # xlim = 0, 104
                    # start = 96
                elif file_name == "random_switch":
                    title = "Random Switch"
                    # xticks = np.arange(0, 104, 10)
                    # xlim = 0, 104
                    # start = 96
                elif file_name == "k_da_anon":
                    title = "K-DA"
                    # xticks = np.arange(1, 25, 1)
                    # xlim = 1, 25
                    # start = 24
                elif file_name == "gen":
                    title = "Generalisation"
                    # xticks = np.arange(0, 120, 10)
                    # xlim = 0, 120
                    # start = 110

                sns.lineplot(x="links_changed", y=__p, data=clean_df, markers=True, dashes=False,
                             label=title, marker='o', color=color, linestyle='None')
                for x, y, z in zip(clean_df["links_changed"], clean_df[__p], clean_df["iteration"]):
                    delta = 4
                    # if __p == "privacy_measure_tim_ipr":
                    #     if file_name == "openstack":
                    #         if "k_da" in file_name:
                    #             delta = 0.00
                    #     if file_name == "apache_flink":
                    #         if "gen" in file_name:
                    #             delta = -0.02
                    #         if "k_da" in file_name and x in [1, 2]:
                    #             delta = -0.02
                    # plt.text(x, y - delta, f'{z}', ha='center', va='bottom', fontsize=10, rotation=45)
                    # if x == 0 or x == size - 1:
                    #     plt.text(x, y + delta, f'{y:.2f}', ha='center', va='bottom', fontsize=10, rotation=45)

            if "privacy" in __p:
                xxminx = minx * 1000
                xxmaxx = maxx

                xstart = xxmaxx - xxmaxx * 0.05
                # plt.plot([0, maxx], [100, 100], color='black', linestyle='dotted', linewidth=line_width)
                # plt.text(xstart, p_l_1, "Privacy Level I", ha='center', va='bottom', fontsize=fontsize_privacy, rotation=0)
                plt.plot([100, maxx], [p_l_2, p_l_2], color='black', linestyle='dotted', linewidth=line_width)
                plt.text(xstart, p_l_2, "Privacy Level I", ha='center', va='bottom', fontsize=fontsize_privacy,
                         rotation=0)
                plt.plot([100, maxx], [p_l_3, p_l_3], color='black', linestyle='dotted', linewidth=line_width)
                plt.text(xstart, p_l_3, "Privacy Level II", ha='center', va='bottom', fontsize=fontsize_privacy,
                         rotation=0)

            if "rf_results" in __p:
                # plt.plot([0, maxx], [baseline_performance, baseline_performance], color='black', linestyle='dotted', linewidth=line_width)
                # for __limit in [800, 90]:
                #     __limit = baseline_performance * __limit
                #     plt.plot([0, maxx], [__limit, __limit], color='black', linestyle='dotted', linewidth=line_width)
                start = clean_df["links_changed"].max()
                for __auc_limits, __auc_label in [(1, "Baseline")]:
                    lower_bound_baseline = baseline_performance * __auc_limits
                    plt.plot([0, maxx], [lower_bound_baseline, lower_bound_baseline],
                             color="black", linestyle='dotted', linewidth=line_width)
                    plt.text(xstart, lower_bound_baseline * 1.025, __auc_label, ha='right', va='center',
                             fontsize=fontsize_privacy)

            xdetla = (maxx - minx) * 0.05
            ydetla = (maxy - miny) * 0.05
            plt.xlim(minx, maxx + xdetla)
            plt.ylim(miny, 105)
            plt.yticks(range(0, 105, 10), rotation=0)
            plt.xlabel("Number of Links Changed", fontsize=fontsize_privacy)

            title = __t.replace("_", " ").title()

            if __p == "rf_results_auc":
                ytitle = "AUC"
            elif __p == "rf_results_rec":
                ytitle = "Recall"
            elif __p == "privacy_measure_tim_ipr":
                ytitle = "IPR"
            elif __p == "privacy_measure_found_percentage":
                ytitle = "Found Percentage"

            plt.ylabel(ytitle, fontsize=fontsize_privacy)

            plt.title(f"{title}")
            plt.xlim(minx, maxx + xdetla)
            plt.xticks(np.arange(minx, maxx + xdetla, xdetla), rotation=25)

            # plt.show()
            plt.rcParams['legend.fontsize'] = fontsize_privacy
            plt.rcParams['legend.title_fontsize'] = fontsize_privacy
            plt.rcParams['axes.labelsize'] = fontsize_privacy
            plt.rcParams['axes.titlesize'] = fontsize_privacy
            plt.rcParams['xtick.labelsize'] = 13
            plt.rcParams['ytick.labelsize'] = fontsize_privacy

            # plt.rcParams.update({'font.size': 30})
            # save fig as
            plt.savefig(f"stat_test/{rq}/{rq}_links_{__t}_{__p}.png", format="png")
            plt.close()
            # plt.close('all')
