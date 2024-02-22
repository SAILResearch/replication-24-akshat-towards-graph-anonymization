import os

import pandas as pd
import matplotlib.pyplot as plt
# import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import numpy as np
import difflib
import kendall_w as kw

from scipy.stats import kendalltau


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

def get_bar_label(col):
    if "la" in col:
        return "blue", "LA"
    if "ld" in col:
        return "orange", "LD"
    if "ent" in col:
        return "green", "ENT"
    if "nf" in col:
        return "red", "NF"
    if "nd" in col:
        return "purple", "ND"
    if "ent" in col:
        return "yellow", "ENT"
    if "nuc" in col:
        return "brown", "NUC"
    if "ndev" in col:
        return "pink", "NDEV"
    if "age" in col:
        return "grey", "AGE"
    if "arexp" in col:
        return "black", "AREXP"
    if "aexp" in col:
        return "cyan", "AEXP"
    if "asexp" in col:
        return "magenta", "ASEXP"



if __name__ == "__main__":

    rq = "data_split_rq3"
    os.makedirs(f"stat_test/{rq}", exist_ok=True)

    clean_result_dir = "../../final_data/rq2"

    dataset_list = ["openstack", "apache_flink", "apache_ignite", "apache_cassandra", "qt", "apache_groovy"]
    technique_name = ["random_add_delete", "random_switch", "k_da_anon", "gen"]

    fontsize_privacy = 18
    linewidth = 3

    for __t in technique_name:

        technique_file_list = []

        for __f in os.listdir(clean_result_dir):
            if __t in __f and "final" in __f and "~$" not in __f and "clean" in __f:
                technique_file_list.append(os.path.join(clean_result_dir, __f))

        if len(technique_file_list) == 0:
            print("Error: cannot find file for technique {}".format(__t))
            continue

        print("Processing {}...".format(__t))

        for __f in technique_file_list:
            label_colors = {}
            minx = 1
            maxx = 0

            miny = 1
            maxy = 0

            plt.rcParams['legend.fontsize'] = fontsize_privacy
            plt.rcParams['legend.title_fontsize'] = fontsize_privacy
            plt.rcParams['axes.labelsize'] = fontsize_privacy
            plt.rcParams['axes.titlesize'] = fontsize_privacy
            plt.rcParams['xtick.labelsize'] = fontsize_privacy
            plt.rcParams['ytick.labelsize'] = fontsize_privacy


            sns.set_theme(style="white", rc={'axes.grid': False})
            fig, ax = plt.subplots(figsize=(15, 8))

            # fig.figure(figsize=(15, 8))

            # label = get_label(__att)

            file_name = os.path.basename(__f).replace("data_split_", "").replace("_train", "")
            __temp_file_name = os.path.basename(file_name).split("_")[0]
            if __temp_file_name == "apache":
                __temp_file_name = os.path.basename(file_name).split("_")[1]
            file_name = __temp_file_name
            clean_df = pd.read_excel(__f)
            # if file_name == "qt":
                # continue

            # f

            print(f"File name: {file_name}")
            clean_df["links_changed"] = clean_df["joined_key"].apply(lambda x: x.split("_")[2])
            clean_df["iteration"] = clean_df["joined_key"].apply(lambda x: x.split("_")[0])
            clean_df["iteration"] = clean_df["iteration"].apply(int)
            # assign each row a number
            clean_df["row_number"] = clean_df.index
            clean_df = clean_df.set_index("joined_key")


            # find first iteration where privacy_percentage went above 0.8 & 0.9
            v80 = clean_df[clean_df["privacy_measure_found_percentage"] > 80]["iteration"].min()
            v90 = clean_df[clean_df["privacy_measure_found_percentage"] > 90]["iteration"].min()

            feat_imp_columns = [x for x in clean_df.columns if "rf_feat_imp" in x]
            clean_df["entropy"] = clean_df[feat_imp_columns].apply(
                lambda x: -sum([(y / 1) * np.emath.logn(len(feat_imp_columns), y / 1) for y in x]), axis=1)

            clean_df["top_5"] = clean_df[feat_imp_columns].apply(lambda x: x.nlargest(5).index.tolist(), axis=1)
            clean_df["top_5_string"] = clean_df["top_5"].apply(lambda x: str(x))
            clean_df["top_5_string"] = clean_df["top_5_string"].apply(lambda x: x.replace("rf_feat_imp_", ""))
            first_row_5 = clean_df[clean_df["iteration"] == -1]["top_5_string"].iloc[0]
            clean_df["edit_distance_5"] = clean_df["top_5_string"].apply(
                lambda x: difflib.SequenceMatcher(None, first_row_5, x).ratio())

            # get first row

            clean_df["all_feats"] = clean_df[feat_imp_columns].apply(lambda x: x.nlargest(len(x) - 1).index.tolist(), axis=1)
            clean_df["all_feats_string"] = clean_df["all_feats"].apply(lambda x: str(x))
            clean_df["all_feats_string"] = clean_df["all_feats_string"].apply(lambda x: x.replace("rf_feat_imp_", ""))
            first_row = clean_df[clean_df["iteration"] == -1]["all_feats_string"].iloc[0]
            clean_df["edit_distance"] = clean_df["all_feats_string"].apply(lambda x: difflib.SequenceMatcher(None, first_row, x).ratio())

            __col_name = "all_feats"
            first_row = clean_df[clean_df["iteration"] == -1][__col_name].iloc[0]
            clean_df["kendalltau_rank"] = clean_df[__col_name].apply(lambda x: kendalltau(first_row, x).correlation)
            # clean_df["kendalltau_rank"] = clean_df[__col_name].apply(lambda x: kw.compute_w([first_row, x]))



            ax.set_yticks([])
            for i, row in clean_df.iterrows():
                width = 0.1
                for j, col in enumerate(row["top_5"]):
                    # print(col)
                    bar_color, bar_label = get_bar_label(col)
                    if bar_label not in label_colors.keys():
                        label_colors[bar_label] = bar_color
                    ax.bar(row["row_number"] + width * j, row[col], width=width, color=bar_color, label=bar_label)
                    ax.set_ylim(0, 1)
                    if j == 0:
                        ax.text(row["row_number"] + width * j, row[col], str(round(row[col], 2)), fontsize=fontsize_privacy)

            ax1 = ax.twinx()
            sns.lineplot(x="row_number", y="rf_results_auc", data=clean_df, label="AUC", ax=ax1, color="red", marker='^',
                         linestyle='solid', linewidth=linewidth)
            # for x, y in zip(clean_df["row_number"], clean_df["rf_results_auc"]):
                # ax1.text(x, y, str(round(y, 2) * 100), fontsize=fontsize_privacy, color="black")
            ax1.set_ylim(-1, 1.2)
            ax1.set_ylabel("AUC & Kendall Tau", fontsize=fontsize_privacy)
            ax1.tick_params(axis='y', rotation=0, labelsize=fontsize_privacy)
            ax1.legend(loc='upper right', bbox_to_anchor=(1.0, 1.0), ncol=1, fontsize= fontsize_privacy)

            # ax2 = ax.twinx()
            # ax2.set_yticks([])
            # sns.lineplot(x="row_number", y="privacy_measure_found_percentage", data=clean_df, label="FP", marker='o', color="green", linestyle='--')
            # for x, y in zip(clean_df["row_number"], clean_df["privacy_measure_found_percentage"]):
            #     ax2.text(x, y, str(round(y, 4)), fontsize=fontsize_privacy, color="green")
            # ax2.set_ylim(0, 1.2)
            # ax2.legend(loc='upper right', bbox_to_anchor=(1.0, 0.95), ncol=1)

            __start_x = -1
            baseline_auc = clean_df["rf_results_auc"].iloc[0] * 0.90
            ax1.axhline(baseline_auc, color="red", linestyle="dotted", linewidth=linewidth)
            # ax1.text(__start_x, baseline_auc, "90% of baseline AUC", fontsize=fontsize_privacy, color="black"                     )

            # baseline_auc = clean_df["rf_results_auc"].iloc[0] * 0.8
            # ax1.axhline(baseline_auc, color="red", linestyle="dotted")
            # ax1.text(__start_x, baseline_auc, "80% of baseline AUC", fontsize=10, color="black")


            ax3 = ax.twinx()
            ax3.set_yticks([])
            __y_axis = "kendalltau_rank"
            sns.lineplot(x="row_number", y=__y_axis, data=clean_df, label="Kendall Rank",
                         marker='o', color="gray", linestyle='solid', linewidth=linewidth)
            # for x, y in zip(clean_df["row_number"], clean_df[__y_axis]):
            #     ax3.text(x, y, str(round(y, 2)), fontsize=fontsize_privacy, color="gray")
            ax3.set_ylim(-1, 1.2)
            ax3.legend(loc='upper right', bbox_to_anchor=(1.0, 0.95), ncol=1, fontsize= fontsize_privacy)

            # ax4 = ax.twinx()
            # ax4.set_yticks([])
            # sns.lineplot(x="row_number", y="edit_distance_5", data=clean_df, label="Edit Distance Top 5", marker='o', color="black", linestyle='--')
            # for x, y in zip(clean_df["row_number"], clean_df["edit_distance_5"]):
            #     ax4.text(x, y, str(round(y, 4)), fontsize=fontsize_privacy, color="black")
            # ax4.set_ylim(0, 1.2)
            # ax4.legend(loc='upper right', bbox_to_anchor=(1.0, 0.85), ncol=1)

            # move legend outside of the plot
            # ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            custom_legend = [plt.Rectangle((0, 0), 1, 1, color=label_colors[label]) for label in label_colors]
            ax.legend(custom_legend, label_colors.keys(), loc="lower right", bbox_to_anchor=(0, 0),
                      fontsize= fontsize_privacy)
            # fig.legend()
            # set xticks to be the row number

            ax.xaxis.set_major_locator(plt.FixedLocator(list(clean_df["row_number"])))
            # clean_df["iteration"] = clean_df["iteration"].apply(str)
            clean_df["iteration"] = clean_df["iteration"].apply(lambda x: f"{x} - PII" if x == v80 else x)
            clean_df["iteration"] = clean_df["iteration"].apply(lambda x: f"{x} - PIII" if x == v90 else x)
            ax.xaxis.set_major_formatter(plt.FixedFormatter(list(clean_df["iteration"])))
            ax.tick_params(axis='x', rotation=0, labelsize=fontsize_privacy)
            # ax.tick_params(axis='y', rotation=0, labelsize=fontsize_privacy)
            __file_name = file_name.title()
            __t_name = __t.split("_")
            __t_name = " ".join(__t_name)
            __t_name = __t_name.title()
            # ax.set_xticks(list(clean_df["row_number"]))
            plt.title(f"{__file_name} -- {__t_name}", fontsize=fontsize_privacy)

            # plt.show()
            fig.savefig(f"stat_test/{rq}/{rq}_{file_name}_{__t}_entropy_auc.svg", format = 'svg')
            plt.close()
