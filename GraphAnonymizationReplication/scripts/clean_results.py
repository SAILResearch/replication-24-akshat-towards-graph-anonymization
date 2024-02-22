import os

import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import numpy as np

# import numpy as np
# import matplotlib.pyplot as plt
# calculate the pareto front
# import pandas as pd


def pareto_front(df, x_col, y_col):
    """
    This function accepts a pandas dataframe and two column names, and returns the Pareto front.
    """
    # Sort the dataframe in descending order of y_col
    df_sorted = df.sort_values(by=y_col, ascending=False)

    # Initialize the Pareto front with the first point
    pareto_front = [df_sorted.iloc[0]]

    # Loop through the dataframe and add points to the Pareto front if they are not dominated
    for i in range(1, len(df_sorted)):
        current_point = df_sorted.iloc[i]
        dominated = False
        for j in range(len(pareto_front)):
            front_point = pareto_front[j]
            if current_point[x_col] <= front_point[x_col] and current_point[y_col] <= front_point[y_col]:
                dominated = True
                break
            elif current_point[x_col] >= front_point[x_col] and current_point[y_col] >= front_point[y_col]:
                pareto_front.pop(j)
                break
        if not dominated:
            pareto_front.append(current_point)

    # Convert the Pareto front back to a dataframe and return it
    pareto_front_df = pd.DataFrame(pareto_front)
    return pareto_front_df


if __name__ == "__main__":

    # file_name = "../final_data/final_openstack_random_add_delete_final_results (3).xlsx"
    # file_name = "../final_data/final_openstack_random_switch_final_results (12).xlsx"
    # file_name = "../final_data/final_openstack_k_da_anon_final_results.xlsx"
    # file_name = "../final_data/final_openstack_gen_final_results.xlsx"

    # file_name = "../final_data/final_apache_flink_random_add_delete_final_results.xlsx"
    # file_name = "../final_data/final_apache_flink_random_switch_final_results.xlsx"
    # file_name = "../final_data/final_apache_flink_k_da_anon_final_results.xlsx"
    # file_name = "../final_data/final_apache_flink_gen_final_results.xlsx"

    # file_name = "../final_data/final_apache_ignite_random_add_delete_final_results.xlsx"
    # file_name = "../final_data/final_apache_ignite_random_switch_final_results.xlsx"
    # file_name = "../final_data/final_apache_ignite_k_da_anon_final_results.xlsx"
    # file_name = "../final_data/final_apache_ignite_gen_final_results.xlsx"

    # file_name = "../final_data/final_apache_cassandra_random_add_delete_final_results.xlsx"
    # file_name = "../final_data/final_apache_cassandra_random_switch_final_results.xlsx"
    # file_name = "../final_data/final_apache_cassandra_k_da_anon_final_results.xlsx"
    #### file_name = "../final_data/final_apache_cassandra_gen_final_results.xlsx"


    # file_name = "../final_data/final_qt_random_switch_final_results.xlsx"
    # file_name = "../final_data/final_qt_random_add_delete_final_results.xlsx"
    # file_name = "../final_data/final_qt_k_da_anon_final_results.xlsx"
    # file_name = "../final_data/final_qt_gen_final_results.xlsx"


    # file_name = "../final_data/final_apache_groovy_random_add_delete_final_results.xlsx"
    # file_name = "../final_data/final_apache_groovy_random_switch_final_results.xlsx"
    # file_name = "../final_data/final_apache_groovy_k_da_anon_final_results.xlsx"
    # file_name = "../final_data/final_apache_groovy_gen_final_results.xlsx"

    # file_name = "../final_data/final_apache_camel_random_add_delete_final_results.xlsx"
    # file_name = "../final_data/final_apache_camel_random_switch_final_results.xlsx"



    # file_name = "../final_data/extra_kda/openstack_k_da_anon_final_results.xlsx"
    # file_name = "../final_data/extra_kda/apache_flink_k_da_anon_final_results.xlsx"
    # file_name = "../final_data/extra_kda/apache_ignite_k_da_anon_final_results.xlsx"


    # file_name = "/Users/maalik/PycharmProjects/GraphAnon/scripts/automation/apache_ignite_random_add_delete_final_results.xlsx"
    # file_name = "/Users/maalik/PycharmProjects/GraphAnon/scripts/automation/openstack_random_add_delete_final_results.xlsx"



    # RQ2

    # file_name = "../final_data/rq2/data_split_apache_ignite_train_random_add_delete_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_openstack_train_random_add_delete_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_apache_flink_train_random_add_delete_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_apache_cassandra_train_random_add_delete_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_qt_train_random_add_delete_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_apache_groovy_train_random_add_delete_final_results.xlsx"

    # file_name = "../final_data/rq2/data_split_openstack_train_k_da_anon_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_apache_ignite_train_k_da_anon_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_apache_flink_train_k_da_anon_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_apache_cassandra_train_k_da_anon_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_qt_train_k_da_anon_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_apache_groovy_train_k_da_anon_final_results.xlsx"

    # file_name = "../final_data/rq2/data_split_apache_ignite_train_gen_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_openstack_train_gen_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_apache_flink_train_gen_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_apache_cassandra_train_gen_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_qt_train_gen_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_apache_groovy_train_gen_final_results.xlsx"

    # file_name = "../final_data/rq2/data_split_apache_ignite_train_random_switch_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_openstack_train_random_switch_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_apache_flink_train_random_switch_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_apache_cassandra_train_random_switch_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_qt_train_random_switch_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_apache_groovy_train_random_switch_final_results.xlsx"

    # file_name = "../sampleData/data_split_apache_ignite_train_random_add_delete_final_results.xlsx"
    # file_name = "../sampleData/data_split_apache_ignite_train_gen_final_results.xlsx"
    # file_name = "../sampleData/data_split_apache_ignite_train_random_switch_final_results.xlsx"
    # file_name = "../sampleData/data_split_apache_ignite_train_k_da_anon_final_results.xlsx"

    # file_name = "../final_data/rq2/data_split_apache_hbase_train_random_add_delete_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_apache_hbase_train_random_switch_final_results.xlsx"
    # file_name = "../final_data/rq2/data_split_apache_hbase_train_k_da_anon_final_results.xlsx"
    file_name = "../final_data/rq2/data_split_apache_hbase_train_gen_final_results.xlsx"



    # file_name = "../sampleData/data_split_apache_ignite_train_k_da_anon_final_results_dummy.xlsx"
    # file_name = "../sampleData/data_split_apache_flink_train_k_da_anon_final_results_dummy.xlsx"
    # file_name = "../sampleData/data_split_apache_cassandra_train_k_da_anon_final_results_dummy.xlsx"
    # file_name = "../sampleData/data_split_openstack_train_k_da_anon_final_results_dummy.xlsx"

    # for file_name in os.listdir("../final_data/rq2/"):
    #
    #     if not file_name.endswith(".xlsx"):
    #         print(file_name)
    #         continue

    # file_name = "../final_data/rq2/" + file_name

    clean_file_name = file_name.replace(".xlsx", "_clean.xlsx")
    print(file_name)

    df = pd.read_excel(file_name)

    parsed_clean_df = pd.DataFrame()

    for index, row in df.iterrows():

        data_dict = {}

        for col in ['rf_results', 'rf_feat_imp', 'privacy_measure']:
            col_val = row[col]
            val_split = col_val.split("\n")
            end_index = len(val_split)
            # if col == 'rf_feat_imp':
            #     end_index = 6
            for val in val_split[1:end_index]:
                print(val)
                val = val.strip()
                __split_val = val.split(" ")
                __split_val[:] = [x for x in __split_val if x]
                print(__split_val)
                index_val = __split_val[0]
                metric_name = __split_val[1]
                metric_val = round(float(__split_val[2]), 4)

                data_dict[col + "_" + metric_name] = metric_val
        print(row["key"])
        # make them cumulative in the code
        data_dict["nodes_changed"] = row["nodes_changed"]
        data_dict["links_changed"] = row["links_changed"]
        data_dict["file_name"] = row["file_name"]
        data_dict["key"] = row["key"]
        data_dict["joined_key"] = str(row["key"]) + "_" + str(row["nodes_changed"]) + "_" + str(row["links_changed"])
        parsed_clean_df = parsed_clean_df.append(data_dict, ignore_index=True)

    columns_list = [
        'rf_results_auc', 'rf_results_pre', "rf_results_rec",
        'privacy_measure_tim_ipr', 'privacy_measure_found_percentage', "privacy_measure_my_ipr_metric",
        # 'graph_privacy_tim_ipr', 'graph_privacy_found_percentage', "graph_privacy_my_ipr_metric",
        "joined_key"
    ]
    df_with_feat_imp = parsed_clean_df.__deepcopy__()



    # parsed_clean_df = parsed_clean_df[columns_list]
    parsed_clean_df.to_excel(clean_file_name)

    # fix, ax = plt.subplots(nrows=3, ncols=1, figsize=(15, 8))
    sns.set_theme(style="darkgrid")

    # Set the figure size and y-axis limits
    plt.figure(figsize=(15, 8))
    plt.ylim(0, 1)

    # Plot the lines and add labels
    for y in ['rf_results_auc', 'rf_results_pre', 'rf_results_rec']:
        if y == 'rf_results_auc':
            label = "AUC"
        elif y == 'rf_results_pre':
            label = "Precision"
        else:
            label = "Recall"
        _ax = sns.lineplot(data=parsed_clean_df, x="joined_key", y=y, markers=True, dashes=False, label=label,
                           marker='o')
        _ax.set_xticklabels(_ax.get_xticklabels(), rotation=40, ha="right")

        # sns.lineplot(data=parsed_clean_df, x="joined_key", y="rf_results_auc", markers=True, dashes=False, label="AUC", marker='o')
        # sns.lineplot(data=parsed_clean_df, x="joined_key", y="rf_results_rec", markers=True, dashes=False, label="Recall", marker='o')

        # Add the value of each point in the line plot
        for x, y1 in zip(parsed_clean_df['joined_key'], parsed_clean_df[y]):
            plt.text(x, y1, f'{y1:.4f}', ha='center', va='bottom', fontsize=10)
            # plt.text(x, y2, f'{y2:.2f}', ha='center', va='top', fontsize=10)

    # Set the x-axis and y-axis labels
    plt.xlabel("Key")
    plt.ylabel("Metric Value")
    plt.tight_layout()

    # Set the y-axis tick marks
    plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1])

    # Create the legend and display the plot
    plt.legend()
    plt.savefig("performance_key_plot.png")

    # reset the figure
    plt.clf()

    plt.ylim(0, 1)
    plt.figure(figsize=(15, 8))
    sns.set_theme(style="darkgrid")

    for y, y_label in [
        ("rf_results_auc", "AUC"),
        # ("rf_results_pre", "Precision"),
        ("rf_results_rec", "Recall"),
        ("privacy_measure_tim_ipr", "Privacy Measure"),
        # ("privacy_measure_my_ipr_metric", "Privacy Measure My IPR Metric"),
        ("privacy_measure_found_percentage", "Privacy Measure Found Percentage"),
        # ("graph_privacy_found_percentage", "Graph Privacy Found Percentage"),
        # ("graph_privacy_my_ipr_metric", "Graph Privacy My IPR Metric")
        # ("graph_privacy_tim_ipr", "Graph Privacy"),
    ]:

        if y == "privacy_measure_my_ipr_metric":
            parsed_clean_df.at[0, "privacy_measure_my_ipr_metric"] = 0

        if y == "graph_privacy_my_ipr_metric":
            parsed_clean_df.at[0, "graph_privacy_my_ipr_metric"] = 0

        _ax = sns.lineplot(data=parsed_clean_df, x="joined_key", y=y, markers=True, dashes=False, label=y_label,
                           marker='o')
        _ax.set_xticklabels(_ax.get_xticklabels(), rotation=40, ha="right")
        for x, y1 in zip(parsed_clean_df['joined_key'], parsed_clean_df[y]):
            plt.text(x, y1, f'{y1:.4f}', ha='center', va='bottom', fontsize=10)

    plt.xlabel("Key")
    plt.ylabel("Metric Value")
    # Set the y-axis tick marks
    plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
    # Create the legend and display the plot
    plt.legend()
    plt.tight_layout()
    plt.savefig("auc_privacy.png")
    # plt.show()

    # main_figure.add_scatter(px.line(parsed_clean_df, x="rf_results_auc", y="rf_results_pre", color="joined_key"))

    plt.clf()

    fig, ax = plt.subplots(figsize=(15, 8))

    # print(feat_imp_columns)
    df_with_feat_imp = df_with_feat_imp.set_index("joined_key")
    feat_imp_columns = [x for x in df_with_feat_imp.columns if "rf_feat_imp" in x]
    all_df_with_feat_imp = df_with_feat_imp.__deepcopy__()
    # all_df_with_feat_imp = all_df_with_feat_imp.set_index("joined_key")
    all_df_with_feat_imp = all_df_with_feat_imp[feat_imp_columns]

    # feat_imp_columns.append("joined_key")
    print(feat_imp_columns)

    __subset_list = []
    __main_index = None

    for __index in df_with_feat_imp.index:
        if "-1" in __index or "1" in __index or "0" in __index:
            __main_index = __index
    if __main_index is None:
        raise Exception("No main index found")

    feat_imp_columns = list(df_with_feat_imp.loc[__main_index][feat_imp_columns][0:6].index)

    df_with_feat_imp = df_with_feat_imp[feat_imp_columns]
    plt.tight_layout()

    # rename the columns
    df_with_feat_imp.columns = [x.split("_")[-1] for x in feat_imp_columns]

    # 2d array for the bar width
    width = 0.10
    arr = []
    arr.append(np.arange(len(df_with_feat_imp.index)))
    for i in range(1, len(df_with_feat_imp.columns)):
        arr.append([x + (width + 0.05) for x in arr[i - 1]])

    for i in range(len(df_with_feat_imp.columns)):
        col = df_with_feat_imp.columns[i]
        ax.bar(arr[i], df_with_feat_imp[col], label=col, width=width)
        for x, y in zip(arr[i], df_with_feat_imp[col]):
            # rotate=45
            ax.text(x, y, f'{y:.4f}', ha='center', va='bottom', fontsize=10, rotation=45)

    # for index, row in df_with_feat_imp.iterrows():
    #     row_total = row.sum()
    #     # calculate entropy
    #     log_base = 6
    #     # perform log with log_base
    #     # df_entropy = df_with_feat_imp.apply(lambda x: -sum([y / row_total * np.log(y / row_total) / np.log(log_base) for y in x]), axis=1)
    #
    #     df_entropy = df_with_feat_imp.apply(lambda x: -sum([y / row_total * np.emath.logn(log_base, y / row_total) for y in x]), axis=1)
        # divide by log2 of the number of classes ahmed icse 2009 paper

    for index, row in all_df_with_feat_imp.iterrows():
        row_total = row.sum()
        log_base = len(row)
        df_entropy = all_df_with_feat_imp.apply(lambda x: -sum([(y / row_total) * np.emath.logn(log_base, y / row_total) for y in x]), axis=1)

    # sns.lineplot(data=parsed_clean_df, x="joined_key", y=y, markers=True, dashes=False, label=label, marker='o', secondary_y=True)
    ax1 = ax.twinx()
    ax1.plot(parsed_clean_df["joined_key"], parsed_clean_df["rf_results_auc"], color="black", marker="o", markersize=4,
             linestyle="dashed", linewidth=2, label="AUC")
    # plot the entropy

    for x, y in zip(parsed_clean_df["joined_key"], parsed_clean_df["rf_results_auc"]):
        ax1.text(x, y, f'{y:.4f}', ha='center', va='bottom', fontsize=10, rotation=45, color="red")

    ax2 = ax.twinx()
    ax2.plot(parsed_clean_df["joined_key"], df_entropy, color="blue", marker="o", markersize=4,
                linestyle="dashed", linewidth=2, label="Entropy")

    for x, y in zip(parsed_clean_df["joined_key"], df_entropy):
        ax2.text(x, y, f'{y:.4f}', ha='center', va='bottom', fontsize=10, rotation=45, color="blue")

    ax.set_xticks(ticks=np.arange(len(df_with_feat_imp.index)), labels=df_with_feat_imp.index, rotation=45)
    ax.set_xlabel("Key")
    ax.set_ylabel("Feature Importance")
    ax1.set_ylabel("AUC")
    ax.legend()
    fig.subplots_adjust(bottom=0.15)
    fig.savefig(f"feat_imp.png")
    # plt.show()

    print(df.columns)

"""Index(['Unnamed: 0', 'key', 'file_name',, 'nodes_altered', 'links_altered'],
      dtype='object')"""

"""'  metric     value
0    auc  0.673061
1     f1  0.280969
2    pre  0.179988
3    acc  0.700000
4    rec  0.640082'"""
