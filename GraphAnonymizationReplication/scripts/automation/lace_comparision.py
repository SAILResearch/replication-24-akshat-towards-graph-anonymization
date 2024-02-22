import os
import sys
import multiprocessing
import time

import pandas as pd

from p2.rf_predictor import run_prediction_cross
from scripts.privacyMeasures.common_measure_privacy import PrivacyMeasurer

import warnings
warnings.filterwarnings("ignore")

def generate_stats(tech, i, df_lace_comp, csv_privacy_measure, df_split_boot_train, df_split_boot_test, bootstrap_column_name):

    os.makedirs("temp", exist_ok=True)


    print(f"collect_everything os id {os.getpid()}")

    if tech == "do_cliff" and i == 0:
        return

    __df = df_lace_comp[(df_lace_comp["technique_id"] == tech) & (df_lace_comp["iteration_id"] == i)]

    data_dict = {}
    data_dict["technique_id"] = tech
    data_dict["iteration_id"] = i
    data_dict["value_id"] = __df["vals_used"].iloc[0]

    __train_df = __df[__df["type_id"] == "train"]
    __test_df = __df[__df["type_id"] == "test"]

    __p_check = __df[__df["type_id"] == "privacy_check"]



    results_store = []
    splits = 0
    for __v in df_split_boot_train[bootstrap_column_name].unique().tolist():
        print(__v)
        splits += 1

        __cur_train_df = df_split_boot_train[df_split_boot_train[bootstrap_column_name] == __v]
        __cur_test_df = df_split_boot_test[df_split_boot_test[bootstrap_column_name] == __v]

        same_ids = __cur_train_df[__cur_train_df["commit_id"].isin(__cur_test_df["commit_id"])]
        print(f"same ids {len(same_ids)}")

        # df_test = df_base[df_base["commit_id"].isin(__cur_test_df["commit_id"])]

        df_train = __train_df.sample(n=500, replace=True)

        print(f"number of same ids {len(df_train[df_train['commit_id'].isin(__cur_test_df['commit_id'])])}")

        try:
            rf_results, lr_results, rf_feat_imp, lr_feat_imp = run_prediction_cross(df_train, __cur_test_df, False)
            # print(f"key {key}")
            print(rf_results)
            results_store.append((rf_results, lr_results, rf_feat_imp, lr_feat_imp))
        except Exception as e:
            splits -= 1
            print(e)
            continue

    rf_results_avg, rf_feat_imp_avg = {}, {}
    for __x in results_store:
        for k in __x[0]:
            rf_results_avg[k] = rf_results_avg.get(k, 0) + __x[0].get(k, 0)
        for k in __x[2]:
            rf_feat_imp_avg[k] = rf_feat_imp_avg.get(k, 0) + __x[2].get(k, 0)
    rf_results_avg = {k: rf_results_avg[k] / splits for k in rf_results_avg}
    rf_feat_imp_avg = {k: rf_feat_imp_avg[k] / splits for k in rf_feat_imp_avg}

    data_dict["rf_results_avg"] = rf_results_avg
    data_dict["rf_feat_imp_avg"] = rf_feat_imp_avg

    print("technique")
    print(tech)
    print("results")
    print(rf_results_avg)


    temp_file_name = "temp/temp_" + str(os.getpid()) + ".csv"
    __p_check.to_csv(temp_file_name, index=False)
    print(tech)
    __res = csv_privacy_measure.measure_privacy(temp_file_name)
    print(__res)
    data_dict["privacy"] = __res


    return data_dict



if __name__ == "__main__":

    # main_dir = "/Users/maalik/PycharmProjects/GraphAnon/lace_test/datasets/"

    base_project_name = sys.argv[1]
    base_project_name_file = base_project_name + ".csv"
    project_name_split_train = "data_split_" + base_project_name +  "_train.csv"
    project_name_split_test = "data_split_" + base_project_name  + "_test.csv"

    project_name_split_train_bootstrap = "data_split_" + base_project_name + "_train_bootstrap.csv"
    project_name_split_test_bootstrap = "data_split_" + base_project_name + "_test_bootstrap.csv"

    lace_comp_file = base_project_name + "_all_comp.csv"

    df_base = pd.read_csv("lace_data/" + base_project_name_file)
    # TODO change this to have only ids that are in 80%



    df_split_train = pd.read_csv(project_name_split_train)
    df_split_test = pd.read_csv(project_name_split_test)
    df_split_boot_train = pd.read_csv(project_name_split_train_bootstrap)
    df_split_boot_test = pd.read_csv(project_name_split_test_bootstrap)

    df_base = df_base[df_base["commit_id"].isin(df_split_train["commit_id"])]

    df_lace_comp = pd.read_csv(lace_comp_file)

    print(base_project_name)
    print(base_project_name_file)
    print(project_name_split_train)
    print(project_name_split_test)


    # measure all the privacy
    csv_privacy_measure = PrivacyMeasurer(
        ["nf", 'nd', 'ns', 'ent', 'ndev', 'nuc', 'age', 'aexp', 'asexp', 'arexp'],
        # ['ent', 'ndev', 'nuc', 'age', 'aexp', 'asexp', 'arexp'],
        ["la", "ld"],
        base_project_name_file,
        {1: 100, 2: 1000, 4: 1000}
    )

    unique_techniques = df_lace_comp["technique_id"].unique().tolist()

    df_lace_comp = df_lace_comp.drop(columns=["Unnamed: 0", "fixcount", "project",
                                    "buggy", "fix", "year",
                                    "osawr", 'author_date',
    'asawr', 'rsawr'], errors="ignore")

    df_lace_comp["author_date"] = pd.merge(df_lace_comp, df_base, on="commit_id")["author_date"]
    df_lace_comp["author_date"].fillna(0, inplace=True)

    bootstrap_column_name = "bootstrap_id"

    tech_results = []
    unique_techniques = ["do_lace2", "do_lace1", "do_morph"]
    for tech in unique_techniques:

        __df = df_lace_comp[df_lace_comp["technique_id"] == tech]

        iterations = __df["iteration_id"].unique().tolist()

        paramters_list = [
            (tech, i, df_lace_comp.__deepcopy__(), csv_privacy_measure, df_split_boot_train.__deepcopy__(),
             df_split_boot_test.__deepcopy__(), bootstrap_column_name)
            for i in iterations
        ]
        # print(paramters_list)

        with multiprocessing.Pool(processes=len(iterations)) as pool:
            results = pool.starmap(generate_stats, paramters_list)

        for r in results:
            tech_results.append(r)

    pd.DataFrame(tech_results).to_excel(f"{base_project_name}_lace_results.xlsx", index=False)

    # # get the bootstrapped performace
    #
    #
    # main_files = []
    #
    # # get the main files in each, like openstack and ignite
    # files = os.listdir(main_dir)
    # for f in files:
    #     if "_" not in f:
    #         main_files.append(f)
    #
    # data_lists = []
    # # for each main file, find the other dependent file,
    # # openstack_lace.csv, openstack_lace_1.csv, openstack_lace_2.csv, openstack_lace_4.csv
    # for m_f in main_files:
    #     m_f_name = m_f.split(".")[0]
    #     print(m_f)
    #     data = {}
    #
    #     data["file_name"] = m_f_name
    #     m_f_path = os.path.join(main_dir, m_f)
    #     print(m_f_path)
    #
    #     # rf_results, _, _, _ = run_prediction_cross(m_f_path, skip_lr=True, optimise_rf=False)
    #     # data["baseline_rf"] = rf_results
    #
    #     csv_privacy_measure = PrivacyMeasurer(
    #         ["nf", 'nd', 'ns', 'ent', 'ndev', 'nuc', 'age', 'aexp', 'asexp', 'arexp'],
    #         ["la", "ld"],
    #         m_f_path,
    #         {1: 100, 2: 1000, 4: 1000}
    #     )
    #
    #     for os_f in os.listdir(main_dir):
    #         if m_f_name in os_f and "_" in os_f:
    #             technique = os_f.split("_")[1].split(".")[0]
    #             current_file = os.path.join(main_dir, os_f)
    #             print(current_file)
    #
    #             # make columns 18 to string when reading the csv
    #             df_main = pd.read_csv(current_file)
    #             df_main["iteration"] = df_main["iteration"].astype(str)
    #
    #             results_store = []
    #             for i in range(10):
    #                 print(f"iteration {i}")
    #                 df_train = df_main[(df_main["iteration"] == str(i)) & (df_main["type"] == "train")]
    #                 df_test = df_main[(df_main["iteration"] == str(i)) & (df_main["type"] == "test")]
    #
    #                 # remove the iteration and type column
    #                 df_train = df_train.drop(["iteration", "type"], axis=1)
    #                 df_test = df_test.drop(["iteration", "type"], axis=1)
    #
    #                 rf_results, lr_results, rf_feat_imp, lr_feat_imp = run_prediction_cross(df_train, df_test, False)
    #                 print(rf_results)
    #                 results_store.append((rf_results, lr_results, rf_feat_imp, lr_feat_imp))
    #
    #                 # break
    #             print("agg results")
    #             rf_results_avg, rf_feat_imp_avg = {}, {}
    #             for __x in results_store:
    #                 for k in __x[0]:
    #                     rf_results_avg[k] = rf_results_avg.get(k, 0) + __x[0].get(k, 0)
    #                 for k in __x[2]:
    #                     rf_feat_imp_avg[k] = rf_feat_imp_avg.get(k, 0) + __x[2].get(k, 0)
    #             rf_results_avg = {k: rf_results_avg[k] / 10 for k in rf_results_avg}
    #             rf_feat_imp_avg = {k: rf_feat_imp_avg[k] / 10 for k in rf_feat_imp_avg}
    #
    #             df_privacy = df_main[df_main["iteration"] == "entire"]
    #             df_privacy = df_privacy[df_privacy["type"] == "privacy"]
    #
    #             df_privacy = df_privacy.drop(["iteration", "type"], axis=1)
    #
    #             # print("calculating privacy")
    #             # df_privacy.to_csv("temp.csv", index=False)
    #             # privacy_measure = csv_privacy_measure.measure_privacy("temp.csv")
    #             # data[technique + "_privacy"] = privacy_measure
    #
    #             print(data)
    #
    #     data_lists.append(data)
    #     # break
    # __save = pd.DataFrame(data_lists)
    # __save.to_csv("lace_comparison.csv", index=False)
    #
