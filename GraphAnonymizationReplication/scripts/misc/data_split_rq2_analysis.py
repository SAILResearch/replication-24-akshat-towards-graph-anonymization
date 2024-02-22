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

    pl1 = 40
    pl2 = 65
    pl3 = 80

    per_lim_1 = 0.95
    per_lim_2 = 0.90

    fontsize_privacy = 18
    linewidth = 3
    markersize = 60

    rq = "data_split_rq2"
    os.makedirs(f"stat_test/{rq}", exist_ok=True)

    clean_result_dir = "../../final_data/rq2"

    dataset_list = ["openstack", "apache_flink", "apache_ignite", "apache_cassandra", "qt", "apache_groovy"]
    technique_name = ["random_add_delete", "random_switch", "k_da_anon", "gen"]

    for __t in technique_name:

        technique_file_list = []

        for __f in os.listdir(clean_result_dir):
            if __t in __f and "final" in __f and "~$" not in __f and "clean" in __f:
                technique_file_list.append(os.path.join(clean_result_dir, __f))

        if len(technique_file_list) == 0:
            print("Error: cannot find file for technique {}".format(__t))
            continue

        print("Processing {}...".format(__t))

        for __att in ["rf_results_auc", "rf_results_rec", "rf_results_pre"]:

            minx = 0
            maxx = 100

            miny = 50
            if __att == "rf_results_rec":
                miny = 0
            maxy = 100

            sns.set_theme(style="darkgrid")
            plt.figure(figsize=(15, 8))

            plt.rcParams['legend.fontsize'] = fontsize_privacy
            plt.rcParams['legend.title_fontsize'] = fontsize_privacy
            plt.rcParams['axes.labelsize'] = fontsize_privacy
            plt.rcParams['axes.titlesize'] = fontsize_privacy
            plt.rcParams['xtick.labelsize'] = fontsize_privacy
            plt.rcParams['ytick.labelsize'] = fontsize_privacy

            label = get_label(__att)

            for __f in technique_file_list:
                file_name = os.path.basename(__f).replace("data_split_", "").replace("_train", "")
                __temp_file_name = os.path.basename(file_name).split("_")[0]
                if __temp_file_name == "apache":
                    __temp_file_name = os.path.basename(file_name).split("_")[1]
                file_name = __temp_file_name
                clean_df = pd.read_excel(__f)

                # if file_name == "qt" or file_name == "groovy":
                #     continue

                # if file_name not in ["openstack", "ignite"]:
                #     continue

                clean_df[__att] = clean_df[__att].astype(float)
                clean_df[__att] = clean_df[__att] * 100

                print(f"File name: {file_name}")
                clean_df["links_changed"] = clean_df["joined_key"].apply(lambda x: x.split("_")[2])
                clean_df["iteration"] = clean_df["joined_key"].apply(lambda x: x.split("_")[0])
                # assign each row a number
                clean_df["row_number"] = clean_df.index
                # clean_df["privacy_average"] = clean_df.apply(
                #     lambda x: round((x["privacy_measure_tim_ipr"] + x["privacy_measure_tim_ipr"]) / 2, 4),
                #     axis=1)
                # line plot for each file with different colors
                # remove 0 links changed

                xaxis = "privacy_measure_tim_ipr"
                yaxis = __att


                clean_df[xaxis] = clean_df[xaxis].astype(float)
                clean_df[xaxis] = clean_df[xaxis] * 100


                baseline_auc = clean_df[clean_df["row_number"] == 0][yaxis].values[0]

                clean_df = clean_df[clean_df["links_changed"] != "0"]
                clean_df = clean_df[clean_df["links_changed"] != "nan"]
                clean_df["links_changed"] = clean_df["links_changed"].astype(float)


                # if clean_df[yaxis].min() < miny:
                #     miny = clean_df[yaxis].min()
                # if clean_df[yaxis].max() > maxy:
                #     maxy = clean_df[yaxis].max()

                # if clean_df[xaxis].min() < minx:
                #     minx = clean_df[xaxis].min()
                # if clean_df[xaxis].max() > maxx:
                #     maxx = clean_df[xaxis].max()


                if file_name.__contains__("openstack"):
                    color = "red"
                    label = "OpenStack"
                if file_name.__contains__("flink"):
                    color = "blue"
                    label = "Apache Flink"
                if file_name.__contains__("ignite"):
                    color = "green"
                    label = "Apache Ignite"
                if file_name.__contains__("cassandra"):
                    color = "orange"
                    label = "Apache Cassandra"
                if file_name.__contains__("qt"):
                    label = "QT"
                    color = "pink"
                if file_name.__contains__("groovy"):
                    label = "Groovy"
                    color = "purple"

                delta_for_baseline = 4
                plt.plot([clean_df[xaxis].min() - delta_for_baseline,
                          clean_df[xaxis].max() + delta_for_baseline], [baseline_auc, baseline_auc], color=color,
                         linestyle='solid', linewidth=linewidth)

                # lower_bound_baseline = baseline_auc * per_lim_1
                # plt.plot([clean_df[xaxis].min() - delta_for_baseline,
                #           clean_df[xaxis].max() + delta_for_baseline], [lower_bound_baseline, lower_bound_baseline],
                #          color=color, linestyle='dotted', linewidth=linewidth)
                # lower_bound_baseline = baseline_auc * 0.80
                # plt.plot([clean_df[xaxis].min() - delta_for_baseline,
                #           clean_df[xaxis].max() + delta_for_baseline], [lower_bound_baseline, lower_bound_baseline],
                #          color=color, linestyle='dotted')
                # upper_bound_baseline = baseline_auc * 1.02
                # plt.plot([clean_df[xaxis].min() - delta_for_baseline,
                #           clean_df[xaxis].max() + delta_for_baseline], [upper_bound_baseline, upper_bound_baseline],
                #          color=color, linestyle="solid")

                # draw a straight line
                # plt.plot([minx, maxx], [baseline_auc, baseline_auc], color='red', linestyle='--')

                # sns.lineplot(x=xaxis, y=__att, data=clean_df, markers=True, dashes=False,
                #              label=label, marker='o', color=color)
                sns.scatterplot(x=xaxis, y=__att, data=clean_df,
                             label=label, marker='o', color=color, s=markersize)

                # for x, y1, w in zip(clean_df[xaxis], clean_df[__att], clean_df["iteration"]):
                #     plt.text(x, y1, f'{w}', ha='center', va='bottom', fontsize=10)

                # sns.lineplot(x="iteration", y="privacy_measure_tim_ipr", data=clean_df, markers=True, dashes=True,
                #              label=label + "Privacy Average", marker='^', color=color, linestyle='dashed')
                # for x, y1 in zip(clean_df["iteration"], clean_df["privacy_measure_tim_ipr"]):
                #     plt.text(x, y1, f'{y1:.4f}', ha='center', va='bottom', fontsize=10)

            # start_y = 100
            # if __att == "rf_results_rec":
            #     start_y = 20
            # plt.text(60, start_y, "Privacy Level I", ha='center', va='top', fontsize=fontsize_privacy, rotation=90)
            # for __privacy_limits, __privacy_label in [(90, "Privacy Level III"), (80, "Privacy Level II"), ]:
            #     plt.plot([__privacy_limits, __privacy_limits], [0, 100], color='black', linestyle='dotted', linewidth=linewidth)
            #     plt.text(__privacy_limits+2, start_y, __privacy_label, ha='center', va='top',
            #              rotation = 90, fontsize=fontsize_privacy)

            y_start_privacy = 100
            if __att == "rf_results_rec":
                y_start_privacy = 20
            # plt.text(pl1, y_start_privacy, "Privacy Level I", ha='center', va='top', fontsize=fontsize_privacy, rotation=90)
            for __privacy_limits, __privacy_label in [(pl3, "Privacy Level II"), (pl2, "Privacy Level I"), ]:
                plt.plot([__privacy_limits, __privacy_limits], [miny, maxy], color='black', linestyle='dotted')
                plt.text(__privacy_limits + 2, y_start_privacy, __privacy_label, ha='center', va='top',
                         rotation=90, fontsize=fontsize_privacy)

            xdelta = (maxx - minx) / 10
            ydelta = (maxy - miny) / 10
            title = __t.split('_')
            title = " ".join(title)
            title = title.title()
            plt.title(f"{title}", fontsize=fontsize_privacy)
            plt.ylim(miny - ydelta, maxy + ydelta)
            plt.yticks([round(i, 4) for i in np.arange(miny, maxy + ydelta, ydelta)], fontsize=fontsize_privacy)
            plt.xticks([round(i, 4) for i in np.arange(minx, maxx + xdelta, xdelta)], fontsize=fontsize_privacy)
            plt.xlim(minx - xdelta, maxx + xdelta)
            plt.xlabel("Privacy Measure IPR", fontsize=fontsize_privacy)
            plt.ylabel(get_label(__att), fontsize=fontsize_privacy)
            plt.legend(loc="lower left", fontsize=fontsize_privacy)
            # plt.show()
            plt.savefig(f"stat_test/{rq}/rq2_{__t}_{__att}_overall.png", format="png")

    for __d in dataset_list:

        file_list = []

        for __cf in os.listdir(clean_result_dir):
            if __d in __cf and "final" in __cf and "~$" not in __cf and "clean" in __cf:
                file_list.append(os.path.join(clean_result_dir, __cf))

        if len(file_list) == 0:
            print("Error: cannot find file for technique {}".format(__d))
            continue

        print("Processing {}...".format(__d))

        for __perf in ["rf_results_auc", "rf_results_rec"]:


            sns.set_theme(style="darkgrid")
            plt.figure(figsize=(15, 8))
            plt.ylim(0, 1)

            plt.rcParams['legend.fontsize'] = fontsize_privacy
            plt.rcParams['legend.title_fontsize'] = fontsize_privacy
            plt.rcParams['axes.labelsize'] = fontsize_privacy
            plt.rcParams['axes.titlesize'] = fontsize_privacy
            plt.rcParams['xtick.labelsize'] = fontsize_privacy
            plt.rcParams['ytick.labelsize'] = fontsize_privacy

            minx = 0
            maxx = 100


            miny = 0
            maxy = 100
            if __perf == "rf_results_rec":
                miny = 0
                maxy = 100

            baseline_auc = None

            for __file in file_list:

                clean_df = pd.read_excel(__file)

                file_name = os.path.basename(__file).replace("data_split_", "").replace("_train", "")
                file_name = \
                    os.path.basename(file_name).replace("final_", "").replace(__d + "_", "").replace("_results",
                                                                                                     "").replace(
                        "_clean.xlsx", "").split(" ")[0]

                clean_df[__perf] = clean_df[__perf].astype(float)
                clean_df[__perf] = clean_df[__perf] * 100

                clean_df["privacy_average"] = clean_df.apply(
                    lambda x: round((x["privacy_measure_tim_ipr"] + x["privacy_measure_tim_ipr"]) / 2, 4), axis=1)
                clean_df["links_changed"] = clean_df["joined_key"].apply(lambda x: x.split("_")[2])
                clean_df["iteration"] = clean_df["joined_key"].apply(lambda x: x.split("_")[0])

                if baseline_auc is None:
                    baseline_auc = clean_df[clean_df["iteration"] == "-1"][__perf].values[0]

                # remove 0 links changed
                clean_df = clean_df[clean_df["links_changed"] != "0"]
                clean_df = clean_df[clean_df["links_changed"] != "nan"]
                clean_df["links_changed"] = clean_df["links_changed"].astype(float)

                xaxis = "privacy_measure_tim_ipr"
                yaxis = __perf

                clean_df[xaxis] = clean_df[xaxis].astype(float)
                clean_df[xaxis] = clean_df[xaxis] * 100


                # if clean_df[yaxis].min() < miny:
                #     miny = clean_df[yaxis].min()
                # if clean_df[yaxis].max() > maxy:
                #     maxy = clean_df[yaxis].max()

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



                sns.scatterplot(x=xaxis, y=yaxis, data=clean_df, label=file_name, color=color, linewidth=linewidth)
                # for x, y1, z in zip(clean_df[xaxis], clean_df[yaxis], clean_df["iteration"]):
                #     plt.text(x, y1, f'{z}', ha='center', va='bottom', fontsize=10)

            # draw a straight line
            minx = 0
            delta_for_baseline = (maxx - minx) / 20

            # plt.text(pl1, 110, "Privacy Level I", ha='center', va='top', fontsize=fontsize_privacy, rotation=90)
            for __privacy_limits, __privacy_label in [(pl3, "Privacy Level II"), (pl2, "Privacy Level I"), ]:
                plt.plot([__privacy_limits, __privacy_limits], [miny, maxy], color='black', linestyle='dotted')
                plt.text(__privacy_limits+2, 110, __privacy_label, ha='center', va='top',
                         rotation = 90, fontsize=fontsize_privacy)

            # baseline_privacy = 0.8
            # plt.plot([baseline_privacy, baseline_privacy], [miny, maxy], color='black', linestyle='dotted')
            plt.plot([minx, maxx], [baseline_auc, baseline_auc], color='black', linestyle='dotted')
            plt.text(minx + delta_for_baseline*2.5, baseline_auc*1.03, "Baseline", ha='right', va='center',
                     fontsize=fontsize_privacy)
            for __auc_limits, __auc_label in [(per_lim_1, f"{per_lim_1*100} % Baseline"), (per_lim_2, f"{per_lim_2*100} % Baseline"), ]:
                lower_bound_baseline = baseline_auc * __auc_limits
                plt.plot([minx - delta_for_baseline,
                          maxx + delta_for_baseline], [lower_bound_baseline, lower_bound_baseline],
                         color="black", linestyle='dotted')
                plt.text(minx + delta_for_baseline*2.5, lower_bound_baseline*1.03, __auc_label, ha='right',
                         va='center', fontsize=fontsize_privacy)

            tick_spacing = 10
            y_ticks = 10

            # xtick_spacing = 2
            # if __perf == "rf_results_rec":
            y_ticks = 10
            xticks = np.arange(minx, maxx + tick_spacing, tick_spacing)
            xticks = [round(x, 2) for x in xticks]
            plt.yticks(np.arange(miny, maxy + y_ticks, y_ticks), fontsize=fontsize_privacy)
            plt.xticks(xticks, rotation=0, fontsize=fontsize_privacy)
            plt.ylim(miny, maxy + y_ticks)
            plt.xlim(minx, maxx + tick_spacing)

            # move legend to left bottom
            plt.legend(loc="lower left")
            title = __d.split('_')
            title = " ".join(title)
            title = title.title()
            plt.title(f"{title}")
            # if xaxis == "privacy_measure_tim_ipr":
            #     xtitle = "Found Percentage"
            # else:
            xtitle = "IPR"
            if yaxis == "rf_results_rec":
                ytitle = "Recall"
            else:
                ytitle = "AUC"
            plt.xlabel(xtitle, fontsize=fontsize_privacy)
            plt.ylabel(ytitle, fontsize=fontsize_privacy)



            plt.rcParams['legend.fontsize'] = fontsize_privacy
            plt.rcParams['legend.title_fontsize'] = fontsize_privacy
            plt.rcParams['axes.labelsize'] = fontsize_privacy
            plt.rcParams['axes.titlesize'] = fontsize_privacy
            plt.rcParams['xtick.labelsize'] = fontsize_privacy
            plt.rcParams['ytick.labelsize'] = fontsize_privacy

            # plt.show()
            plt.savefig(f"stat_test/{rq}/rq2_{__d}_{__perf}.png", format="png")
