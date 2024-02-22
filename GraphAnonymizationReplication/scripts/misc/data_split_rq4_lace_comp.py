import os

import pandas as pd
import matplotlib.pyplot as plt
# import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import numpy as np

def format_lace_result(df):
    parsed_clean_df = pd.DataFrame()

    for index, row in df.iterrows():

        data_dict = {}

        for col in ['rf_results_avg', 'privacy']:
            col_val = row[col]
            val_split = col_val.replace("\"", "").replace("{", "").replace("}", "").replace("'", "").split(",")

            for val in val_split:
                # print(val)
                val = val.strip()
                __split_val = val.split(":")
                metric_name = __split_val[0]
                metric_val = round(float(__split_val[1]), 4)
                data_dict[col + "_" + metric_name] = metric_val

        # print(row["iteration_id"])
        # make them cumulative in the code
        data_dict["technique_id"] = row["technique_id"]
        data_dict["iteration_id"] = row["iteration_id"]
        data_dict["value_id"] = row["value_id"]
        # data_dict["key"] = row["key"]
        # data_dict["joined_key"] = str(row["key"]) + "_" + str(row["nodes_changed"]) + "_" + str(row["links_changed"])
        parsed_clean_df = parsed_clean_df.append(data_dict, ignore_index=True)

    columns_list = [
        'rf_results_auc', 'rf_results_pre', "rf_results_rec",
        'privacy_measure_tim_ipr', 'privacy_measure_found_percentage', "privacy_measure_my_ipr_metric",
        # 'graph_privacy_tim_ipr', 'graph_privacy_found_percentage', "graph_privacy_my_ipr_metric",
        "joined_key"
    ]

    return parsed_clean_df


def get_color(file_name):
    if "random_add_delete" in file_name:
        color = "red"
    elif "random_switch" in file_name:
        color = "blue"
    elif "gen" in file_name:
        color = "green"
    elif "k_da" in file_name:
        color = "orange"
    elif "morph" in file_name:
        color = "purple"
    elif "lace1" in file_name:
        color = "black"
    elif "lace2" in file_name:
        color = "yellow"
    return color

if __name__ == "__main__":

    datastore = []

    columns_list = ["technique", "dataset", "auc", "rec", "privacy", "iteration"]
    consolidated_df = pd.DataFrame(columns=columns_list)

    pl1 = 40
    pl2 = 65
    pl3 = 80

    per_lim_1 = 0.95
    per_lim_2 = 0.90

    fontsize_privacy = 18
    linewidth = 3
    markersize = 60

    rq = "data_split_rq4_lace_comp"
    os.makedirs(f"stat_test/{rq}", exist_ok=True)

    clean_result_dir = "../../final_data/rq2"
    lace_result_dir = "../../lace_results"

    dataset_list = ["apache_flink", "apache_ignite", "apache_cassandra", "qt", "apache_groovy", "openstack"]
    technique_name = ["random_add_delete", "random_switch", "k_da_anon", "gen"]
    combined_df = pd.DataFrame()

    sns.set_style("darkgrid")

    for __d in dataset_list:

        file_list = []

        for __cf in os.listdir(clean_result_dir):
            if __d in __cf and "final" in __cf and "~$" not in __cf and "clean" in __cf:
                file_list.append(os.path.join(clean_result_dir, __cf))

        if len(file_list) == 0:
            print("Error: cannot find file for technique {}".format(__d))
            continue

        print("Processing data {}...".format(__d))

        for __l_f in os.listdir(lace_result_dir):
            if __d in __l_f:
                lace_file = os.path.join(lace_result_dir, __l_f)
                break

        lace_df = pd.read_excel(lace_file)
        format_lace_df = format_lace_result(lace_df)

        __small_format_lace_df = format_lace_df[["rf_results_avg_auc", "rf_results_avg_rec", "privacy_tim_ipr", "technique_id", "value_id"]]
        __small_format_lace_df["dataset"] = __d
        __small_format_lace_df = __small_format_lace_df.rename(
            columns={"rf_results_avg_auc": "auc", "rf_results_avg_rec": "rec", "privacy_tim_ipr": "privacy", "technique_id" : "technique",
                     "value_id": "iteration"}
        )
        # if __d not in consolidated_df["dataset"].unique() and __small_format_lace_df["technique"] not in consolidated_df["technique"].unique():
        consolidated_df = pd.concat([consolidated_df, __small_format_lace_df], ignore_index=True)



        for __perf in ["rf_results_auc", "rf_results_rec"]:



            # sns.set_theme(style="darkgrid")
            plt.figure(figsize=(15, 8))
            plt.ylim(0, 100)

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
            baseline_rec = None


            for __file in file_list:

                data = {}

                clean_df = pd.read_excel(__file)



                file_name = os.path.basename(__file).replace("data_split_", "").replace("_train", "")
                file_name = \
                    os.path.basename(file_name).replace("final_", "").replace(__d + "_", "").replace("_results",
                                                                                                     "").replace(
                        "_clean.xlsx", "").split(" ")[0]

                print("File name: {}".format(file_name))

                __small_df = clean_df[["rf_results_auc", "rf_results_rec", "privacy_measure_tim_ipr", "key"]]
                __small_df["dataset"] = __d
                __small_df["technique"] = file_name
                __small_df = __small_df.rename(
                    columns={"rf_results_auc": "auc", "rf_results_rec": "rec", "privacy_measure_tim_ipr": "privacy",
                             "key": "iteration"}
                )

                if __d not in consolidated_df["dataset"].unique() and file_name not in consolidated_df["technique"].unique():
                    consolidated_df = pd.concat([consolidated_df, __small_df], ignore_index=True)



                xaxis = "privacy_measure_tim_ipr"
                yaxis = __perf
                color = get_color(file_name)


                clean_df["key"] = clean_df["key"].astype(int)
                # baseline row is where iteration is -1
                baseline_row = clean_df[clean_df["key"] == -1]
                # remove baseline row
                clean_df = clean_df[clean_df["key"] != -1]


                for __col in [xaxis, yaxis]:
                    clean_df[__col] = clean_df[__col].astype(float)
                    clean_df[__col] = clean_df[__col].apply(lambda x: round(x*100, 2))

                # do file vaala here
                # print(clean_df[[xaxis, yaxis]])
                __temp_label = file_name.replace("_", " ").title()
                sns.scatterplot(x=xaxis, y=yaxis, data=clean_df, label=__temp_label, color=color, markers="o", s=markersize)

                y_start_privacy = 100
                if __perf == "rf_results_rec":
                    y_start_privacy = 30
                for __privacy_limits, __privacy_label in [(pl3, "Privacy Level II"), (pl2, "Privacy Level I"), ]:
                    plt.plot([__privacy_limits, __privacy_limits], [miny, maxy], color='black', linestyle='dotted')
                    plt.text(__privacy_limits + 2, y_start_privacy, __privacy_label, ha='center', va='top',
                             rotation=90, fontsize=fontsize_privacy)

                # baseline_measure = baseline_row[xaxis].values[0]
                baseline_perf = baseline_row[yaxis].values[0]

                best_performing = clean_df[clean_df[xaxis] > 80][__perf].median()
                # get the privacy scores for the best performing
                __x = clean_df[clean_df[__perf] == best_performing]
                if len(__x) > 0:
                    best_performing_privacy = __x[xaxis].values[0]
                else:
                    best_performing_privacy = "NA"



                if baseline_auc is None and "auc" in __perf:
                    baseline_auc = baseline_perf
                elif baseline_rec is None and "rec" in __perf:
                    baseline_rec = baseline_perf

                data["technique"] = __temp_label
                data["file"] = file_name
                data["dataset"] = __d
                data["perf"] = __perf
                data["baseline"] = baseline_perf*100
                data["best"] = best_performing
                data["privacy"] = best_performing_privacy
                data["percent_change"] = round((( data["best"] - data["baseline"]) / data["baseline"] ) * 100, 2)
                data["combined"] = f"{data['best']} ({data['percent_change']})"
                datastore.append(data)

                consolidated_df = pd.concat([consolidated_df, __small_df], ignore_index=True)





            for __lace_t in format_lace_df["technique_id"].unique():

                data = {}

                if "auc" in __perf:
                    yaxis = "rf_results_avg_auc"
                elif "rec" in __perf:
                    yaxis = "rf_results_avg_rec"
                xaxis = "privacy_tim_ipr"
                color = get_color(__lace_t)

                __temp_format_lace_df = format_lace_df[format_lace_df["technique_id"] == __lace_t].__deepcopy__()

                for __col in [xaxis, yaxis]:
                    __temp_format_lace_df[__col] = __temp_format_lace_df[__col].astype(float)
                    __temp_format_lace_df[__col] = __temp_format_lace_df[__col].apply(lambda x: round(x * 100, 2))

                # print(__temp_format_lace_df[[xaxis, yaxis]])
                __temp_label = __lace_t.replace("do_", "").upper()
                sns.scatterplot(x=xaxis, y=yaxis, data=__temp_format_lace_df, label=__temp_label, color=color
                                , marker="^", s=markersize)

                if "auc" in __perf:
                    baseline_perf = baseline_auc
                else:
                    baseline_perf = baseline_rec

                best_performing = __temp_format_lace_df[__temp_format_lace_df[xaxis] > 80][yaxis].median()
                # for the above get the privacy score as well
                privacy_score = 0
                if len(__temp_format_lace_df[__temp_format_lace_df[yaxis] == best_performing]) > 0:
                    privacy_score = __temp_format_lace_df[__temp_format_lace_df[yaxis] == best_performing][xaxis].values[0]

                data["technique"] = __lace_t
                data["file"] = ""
                data["dataset"] = __d
                data["perf"] = __perf
                data["baseline"] = baseline_perf*100
                data["best"] = best_performing
                data["privacy"] = privacy_score
                data["percent_change"] = round(((data["best"] - data["baseline"]) / data["baseline"]) * 100, 2)
                data["combined"] = f"{data['best']} ({data['percent_change']})"
                datastore.append(data)


            xtitle = "IPR"
            if "rec" in yaxis:
                ytitle = "Recall"
            else:
                ytitle = "AUC"
            plt.xlabel(xtitle, fontsize=fontsize_privacy)
            plt.ylabel(ytitle, fontsize=fontsize_privacy)
            plt.legend(loc="lower left")


            title = __d.split('_')
            title = " ".join(title)
            title = title.title()
            plt.title(f"{title}")
            # plt.title(__d)
            # plt.show()


            plt.xlim(0, 105)
            plt.ylim(0, 105)
            plt.xticks(np.arange(0, 105, 10))
            plt.yticks(np.arange(0, 105, 10))

            if "auc" in __perf:
                plt.ylim(50, 105)
                plt.yticks(np.arange(50, 105, 10))


            plt.savefig(f"stat_test/{rq}/{__d}_{__perf}_lace.png")


    df = pd.DataFrame(datastore)
    df.to_excel(f"stat_test/{rq}/lace_comp_1.xlsx", index=False)
    plt.close("all")

    # consolidated_df.to_excel(f"stat_test/{rq}/lace_comp_consolidated.xlsx", index=False)

    new_cons_df = pd.DataFrame()
    for __dataset in dataset_list:

        small_df_test = consolidated_df[consolidated_df["dataset"] == __dataset].__deepcopy__()

        baseline_row = small_df_test[small_df_test["iteration"] == -1].head(1)
        baseline_auc = baseline_row["auc"].values[0]
        baseline_rec = baseline_row["rec"].values[0]

        small_df_test["percent_change_auc"] = round(((small_df_test["auc"] - baseline_auc) / baseline_auc) * 100, 2)
        small_df_test["percent_change_rec"] = round(((small_df_test["rec"] - baseline_rec) / baseline_rec) * 100, 2)

        new_cons_df = pd.concat([new_cons_df, small_df_test], ignore_index=True)

    new_cons_df.to_excel(f"stat_test/{rq}/lace_comp_consolidated.xlsx", index=False)









