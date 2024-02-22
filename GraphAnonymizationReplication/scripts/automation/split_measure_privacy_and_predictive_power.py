import os
import sys
import multiprocessing
import time

import pandas as pd

from sklearn.model_selection import StratifiedShuffleSplit

from scripts.jit_defect_model.python_function_for_ac import run_prediction
from scripts.privacyMeasures.common_measure_privacy import PrivacyMeasurer
from scripts.privacyMeasures.jit_data_privacy_measure_tim import (
    generate_dict_store, get_privacy_measure)

from scripts.privacyMeasures import rf_predictor


def collect_everything(key, file_name: str, csv_privacy_measure: PrivacyMeasurer,
                       graph_privacy_measure: PrivacyMeasurer,
                       graph_file_name: str, control_flag: str, __non_anon_file_name, __file_prefix_bootstrap):
    print(f"collect_everything os id {os.getpid()}")
    __fun_start_time = time.time()

    if control_flag == "only_privacy":
        privacy_measure = csv_privacy_measure.measure_privacy(file_name)

        # graph_privacy = graph_privacy_measure.measure_privacy(graph_file_name)
        print("Privacy measure: ", privacy_measure)
        # print("Graph privacy measure: ", graph_privacy)
        return (key, file_name, {}, {}, {}, {}, privacy_measure, {})

    # the current anonymised file
    print(f"file name {file_name}")
    df_anon = pd.read_csv(file_name)
    df_anon = df_anon.dropna(subset=["commit_id"])

    # data_split_apache_camel_train_gen

    # file_prefix = file_prefix.replace("_train", "")
    train_file_name = f"{__file_prefix_bootstrap}_train_bootstrap.csv"
    test_file_name = f"{__file_prefix_bootstrap}_test_bootstrap.csv"
    validation_file_name = f"{__file_prefix_bootstrap}_vali_bootstrap.csv"

    base_non_anon_df = pd.read_csv(__non_anon_file_name)

    bootstrap_df_train = pd.read_csv(train_file_name)
    bootstrap_df_test = pd.read_csv(test_file_name)
    # bootstrap_df_vali = pd.read_csv(validation_file_name)

    # bootstrap_df_test = pd.concat([bootstrap_df_test, bootstrap_df_vali])

    # TODO: SMOTE
    # TODO: TUNING

    bootstrap_column_name = "bootstrap_id"

    results_store = []
    splits = 0
    for __v in bootstrap_df_train[bootstrap_column_name].unique():
        splits += 1
        print(f"bootstrap id {__v} - split {splits}")

        __cur_train_df = bootstrap_df_train[bootstrap_df_train[bootstrap_column_name] == __v]
        __cur_test_df = bootstrap_df_test[bootstrap_df_test[bootstrap_column_name] == __v]

        same_ids = __cur_train_df[__cur_train_df["commit_id"].isin(__cur_test_df["commit_id"])]
        print(f"same ids {len(same_ids)}")

        df_train = df_anon[df_anon["commit_id"].isin(__cur_train_df["commit_id"])]
        df_test = base_non_anon_df[base_non_anon_df["commit_id"].isin(__cur_test_df["commit_id"])]
        print(f"len df train {len(df_train)} - len df test {len(df_test)}")

        rf_results, lr_results, rf_feat_imp, lr_feat_imp = run_prediction_cross(df_train, df_test, False)
        print(f"key {key}")
        print(rf_results)
        results_store.append((rf_results, lr_results, rf_feat_imp, lr_feat_imp))

    rf_results_all = results_store

    rf_results_avg, rf_feat_imp_avg = {}, {}
    for __x in results_store:
        for k in __x[0]:
            rf_results_avg[k] = rf_results_avg.get(k, 0) + __x[0].get(k, 0)
        for k in __x[2]:
            rf_feat_imp_avg[k] = rf_feat_imp_avg.get(k, 0) + __x[2].get(k, 0)
    rf_results_avg = {k: rf_results_avg[k] / splits for k in rf_results_avg}
    rf_feat_imp_avg = {k: rf_feat_imp_avg[k] / splits for k in rf_feat_imp_avg}

    privacy_measure = {"tim_breaches": 0, "tim_total": 0, "tim_ipr": 0, "my_breach_metric": 0, "my_metric_total": 0,
                       "my_ipr_metric": 0, "original_length": 0, "found_length": 0, "found_percentage": 0}
    if key != "non_anon":
        privacy_measure = csv_privacy_measure.measure_privacy(file_name)

    print("Privacy measure: ", privacy_measure)
    print("RF results: ", rf_results_avg)

    __fun_end_time = time.time()
    print(f"os pid {os.getpid()} - time {__fun_end_time - __fun_start_time}")
    return key, file_name, rf_results_avg, {}, rf_feat_imp_avg, {}, privacy_measure, rf_results_all


def get_files(file_directory, file_prefix):
    print("file prefix: ", file_prefix)
    # Get a list of all files in the directory
    all_files = os.listdir(file_directory)

    # Filter the list to include only files with the desired prefix
    filtered_files = [f for f in all_files if f.startswith(file_prefix)]

    files_dict = {}
    for f in filtered_files:
        __index = f
        __index = __index.replace(file_prefix + "_", "")
        __index = __index.split("-")[0]
        __index = __index.split(".")[0]

        files_dict[__index] = os.path.join(file_directory, f)

    # print(files_dict)

    return files_dict


if __name__ == "__main__":
    __entire_start_time = time.time()
    file_prefix = "apache_ignite_random_add_delete"
    file_directory = "/Users/maalik/PycharmProjects/GraphAnon/apache_ignite_random"

    control_flag = ""
    if os.environ.get("run_env") != "local":
        file_prefix = sys.argv[1]
        file_directory = sys.argv[2]
        if len(sys.argv) == 4:
            control_flag = "only_privacy"

    print(f"control_flag: {control_flag}")
    csv_filtered_files = get_files(file_directory, file_prefix)
    df = pd.DataFrame()

    # get original file name
    # data_split_apache_ignite_train_random_add_delete
    original_file_prefix = file_prefix.replace("data_split_", "").replace("_train", "")
    file_split_prefix = original_file_prefix.split("_")

    if "apache" in original_file_prefix:
        __dataset_name = "apache_" + file_split_prefix[1]
        __technique = "_".join(file_split_prefix[2:])
    else:
        __dataset_name = file_split_prefix[0]
        __technique = "_".join(file_split_prefix[1:])

    baseline_file_technique = "k_da_anon"
    print(f"dataset_name: {__dataset_name} - technique: {__technique}")
    __non_anon_file_directory = os.path.join("anon_results", __dataset_name, baseline_file_technique)
    __non_anon_file_prefix = __dataset_name + "_" + baseline_file_technique
    __non_anon_file_name = get_files(__non_anon_file_directory, __non_anon_file_prefix)["non_anon"]
    __non_anon_file_name_path = __non_anon_file_name
    # __non_anon_file_name_path = os.path.join(__non_anon_file_directory, __non_anon_file_name)
    print(f"non anon file name: {__non_anon_file_name}")
    print(f"non anon file name path: {__non_anon_file_name_path}")

    __file_prefix_bootstrap = f"data_split_{__dataset_name}"

    graph_data_prefix = "graph_csv_dump"
    print("graph")
    print(file_directory)

    # graph_filtered_files = get_files(file_directory, graph_data_prefix + "_" + file_prefix)

    csv_privacy_measure = PrivacyMeasurer(
        ["nf", 'nd', 'ns', 'ent', 'ndev', 'nuc', 'age', 'aexp', 'asexp', 'arexp'],
        # ["nf", 'nd', 'ns', 'ent', 'ndev', 'nuc', "age"],  # 'aexp', 'asexp', 'arexp'],
        ["la", "ld"],
        csv_filtered_files["non_anon"],
        {1: 100, 2: 1000, 4: 1000}
    )

    print("here1")

    with multiprocessing.Pool(processes=len(csv_filtered_files.keys())) as csv_pool:
        parameter_list = [
            (key, csv_filtered_files[key], csv_privacy_measure, None, None, control_flag, __non_anon_file_name_path,
             __file_prefix_bootstrap)
            for key in csv_filtered_files.keys()
        ]
        print(parameter_list)
        privacy_measure_scores = csv_pool.starmap(collect_everything, parameter_list)

    print("calculation done, now combining")

    __privacy_measure_time_start = time.time()
    for score in privacy_measure_scores:
        print("score: ", score)
        key, file_name, rf_results, lr_results, rf_feat_imp, lr_feat_imp, privacy_measure, rf_results_all = score
        data_dict = {
            "key": key,
            "file_name": file_name,
            "rf_results": pd.DataFrame(rf_results.items(), columns=["metric", "value"]),
            "rf_feat_imp": pd.DataFrame(rf_feat_imp.items(), columns=["metric", "value"]),
            "privacy_measure": pd.DataFrame(privacy_measure.items(), columns=["metric", "value"]),
            "graph_privacy": pd.DataFrame(),
            "rf_results_all": rf_results_all
        }
        df = pd.concat([df, pd.DataFrame([data_dict])], ignore_index=True)

    __privacy_measure_time_end = time.time()
    print(f"time taken for privacy {__privacy_measure_time_end - __privacy_measure_time_start}")

    # save the results in excel file
    __file_name_save = file_prefix + "_final_results.xlsx"
    print(f"Saving results in file: {__file_name_save}")

    # in column key replace non_anon with -1
    df["key"] = df["key"].replace("non_anon", -1)

    try:
        df["key"] = df["key"].astype(int)
        df = df.sort_values(by=["key"])
    except Exception as e:
        print(e)

    # sort the dataframe by key

    # add two empty columns called nodes_changed and links_changed
    df["nodes_changed"] = ""
    df["links_changed"] = ""

    df.to_excel(__file_name_save)

    __entire_end_time = time.time()
    print(f"Total time taken: {__entire_end_time - __entire_start_time} seconds")
