import concurrent
import os
import random
import time
import pandas as pd
import numpy as np
from dateutil import parser

import datetime

class PrivacyMeasurer:
    
    attributes_for_queries = []
    hidden_attributes = []
    bin_atts = []
    path_to_base_file = None
    
    __query_dict = {}
    
    def __init__(self, attributes_for_queries, hidden_attributes, path_to_base_file, configuration_dict) -> None:
        self.attributes_for_queries = attributes_for_queries
        self.hidden_attributes = hidden_attributes
        self.path_to_base_file = path_to_base_file
        
        self.bin_atts = attributes_for_queries.copy()
        self.bin_atts.extend(hidden_attributes)
        
        self.__query_dict = self.__get_query_dict(configuration_dict)

    def bin_column(self, df):
        df = df.astype(float)
        return pd.qcut(df, 20, duplicates='drop', retbins=True)
    def __get_query_dict(self, configuration_dict):
        
        df_unanonymised = pd.read_csv(self.path_to_base_file)

        for att in self.bin_atts:
            df_unanonymised["att"] = df_unanonymised[att].astype(float)
            df_unanonymised[att + "_binned"], self.__bins = self.bin_column(df_unanonymised[att])
            print("Bins for " + att + " are " + str(self.__bins.size))

        all_dict_store = []
        for keys_len, total_length in configuration_dict.items():
            for _ in range(total_length):
                key_val_store = {}
                df_unanonymised_clone = df_unanonymised.copy()
                attributes_for_queries_clone = self.attributes_for_queries.copy()
                for _ in range(keys_len):
                    count = 30
                    while True:
                        count -= 1
                        if count == 0:
                            print("Could not find a value for attribute")
                            break
                        attr = random.choice(attributes_for_queries_clone)
                        _attr = attr + "_binned"
                        # need complicated query construction
                        valu = random.choice(df_unanonymised_clone[_attr].unique().tolist())
                        if valu not in key_val_store.values() and len(df_unanonymised_clone[df_unanonymised_clone[_attr] == valu]) > 0:
                            key_val_store[_attr] = valu
                            df_unanonymised_clone = df_unanonymised_clone[df_unanonymised_clone[_attr] == valu]
                            attributes_for_queries_clone.remove(attr)
                            break

                all_dict_store.append(key_val_store)

        # print("Len of dict " + str(len(all_dict_store)))
        return all_dict_store
    
    def measure_privacy(self, anon_file_path):
        
        df_anonymised = pd.read_csv(anon_file_path)
        df_unanonymised = pd.read_csv(self.path_to_base_file)
        
        for att in self.bin_atts:
            # df_unanonymised[att + "_binned"], self.__bins = pd.qcut(df_unanonymised[att], 10, retbins=True, duplicates='drop')
            # df_anonymised[att + "_binned"], _ = pd.qcut(df_anonymised[att], 10, retbins=True, duplicates='drop')

            # df_unanonymised[att + "_binned"] = pd.cut(df_unanonymised[att], bins =self.__bins, duplicates='drop')
            # df_anonymised[att + "_binned"] = pd.cut(df_anonymised[att], bins= self.__bins, duplicates='drop')

            df_unanonymised[att + "_binned"], self.__bins = self.bin_column(df_unanonymised[att])
            df_anonymised[att + "_binned"] = pd.cut(df_anonymised[att], bins=self.__bins)


        breach = 0
        total = 0
        my_breach_metric = 0
        my_metric_total = 0
        
        original_length = 0
        found_length = 0
        
        for key_val in self.__query_dict:
            # print("*" * 20)

            df_unanon_duplicate = df_unanonymised.copy(deep=True)
            df_anon_duplicate = df_anonymised.copy(deep=True)

            for key, val in key_val.items():
                # print(f"{key} - {val}")
                non_bin_key = key.replace("_binned", "")

                df_anon_duplicate = df_anon_duplicate[df_anon_duplicate[non_bin_key].between(val.left, val.right, inclusive="right")]
                df_unanon_duplicate = df_unanon_duplicate[df_unanon_duplicate[non_bin_key].between(val.left, val.right, inclusive="right")]

            for sens_att in self.hidden_attributes:
                sens_att += "_binned"

                if not (len(df_unanon_duplicate) > 0):
                    continue
                
                # print("checking len")
                
                df_anon_found = df_anon_duplicate[df_anon_duplicate["commit_id"].isin(df_unanon_duplicate["commit_id"])]
                
                anon_att = df_anon_duplicate[sens_att].value_counts(ascending=True).to_frame().sort_index(ascending=False)
                unanon_att = df_unanon_duplicate[sens_att].value_counts(ascending=True).to_frame().sort_index(ascending=False)
                
                original_length += len(df_unanon_duplicate)
                found_length += len(df_anon_found)
                
                for value in anon_att[sens_att].index:
                    anon_len = len(df_anon_duplicate[df_anon_duplicate[sens_att] == value])
                    unanon_len = len(df_unanon_duplicate[df_unanon_duplicate[sens_att] == value])


                    my_metric_total += 1

                    if anon_len - unanon_len == 0:
                        my_breach_metric += 1
                
                max_anon = -1
                if len(df_anon_duplicate) != 0:
                    max_anon = df_anon_duplicate[sens_att].value_counts(ascending=True).to_frame().index[-1]
                max_un_anon = df_unanon_duplicate[sens_att].value_counts(ascending=True).to_frame().index[-1]

                if max_anon == max_un_anon:
                    breach += 1
                total += 1

        # if breach == 0:
        #     breach = 1
        if total == 0:
            total = 1
        # if my_breach_metric == 0:
        #     my_breach_metric = 0
        if my_metric_total == 0:
            my_metric_total = 1
        
        # print(f"breaches {breach} ipr {1 - (1 / breach)} total {total} another way { 1 - (breach / total)}")
        # print(f"my breach {my_breach_metric} ipr {1 - (1 / my_breach_metric)} total {my_metric_total}")
        # print(f"my ipr {1 - (my_breach_metric / my_metric_total)}")
        # print(f"original length {original_length} found length {found_length} found percentage {found_length / original_length}")
        
        privacy_measure = {
            "tim_breaches": round(breach, 6),
            "tim_total": round(total, 6),
            "tim_ipr": round(1 - (breach / total), 6),

            "my_breach_metric": round(my_breach_metric, 6),
            "my_metric_total": round(my_metric_total, 6),
            "my_ipr_metric": round(my_breach_metric / my_metric_total, 6),
            # "my_ipr": round(1 - (1 / my_breach_metric), 6),

            "original_length": round(original_length, 6),
            "found_length": round(found_length, 6),
            "found_percentage": round(1 - (found_length / original_length), 6)
        }
        print(privacy_measure)
        return privacy_measure
    
    @staticmethod
    def transform_graph_file(args):
        print(f"transform_graph_file - {os.getpid()}")
        start_time = time.time()
        graph_file_path = args[1]
        key_file_path = args[0]
        df = pd.read_csv(graph_file_path)

        # print(df.columns)

        df_nodes = df[df["_id"].notnull()]
        df_relation = df[df["_id"].isnull()]

        df_commits = df[df["_labels"] == ":Commit"]


        # print(df_commits.head())
        # print(df_relation.head())

        df_data = pd.DataFrame()

        start = 300
        parallel_workers = 5
        with concurrent.futures.ThreadPoolExecutor(parallel_workers) as executor:
            future_to_commit = {executor.submit(PrivacyMeasurer.get_data_for_formatted_df, df_nodes, df_relation, row):
                                    row for _, row in df_commits.iterrows()}
            for future in concurrent.futures.as_completed(future_to_commit):
                commit = future_to_commit[future]
                try:
                    data_dict = future.result()
                    df_data = pd.concat([df_data, pd.DataFrame([data_dict])], ignore_index=True)
                except Exception as exc:
                    print(f"{commit} generated an exception: {exc}")
        #
        # for index, row in df_commits.iterrows():
        #
        # 
        #     PrivacyMeasurer.get_data_for_formatted_df(df_nodes, df_relation, row)
        #
        #     df_data = df_data.append(data_dict, ignore_index=True)

        # print(df_data.head())
        file_name = os.path.dirname(graph_file_path) + "/" + f"formatted_data_{datetime.datetime.now()}.csv"
        df_data.to_csv(file_name)
        end_time = time.time()
        print(f"{os.getpid()} - {end_time - start_time}")
        return file_name, key_file_path

    @staticmethod
    def get_data_for_formatted_df(df_nodes, df_relation, row):
        start_time = time.time()
        data_dict = {"commit": row["id"], "la": 0, "ld": 0, "author_date": row["author_date"]}
        # check for null
        # data_dict["la"] = int(row["la"]) if not np.isnan(row["la"]) else 0
        # data_dict["ld"] = int(row["ld"]) if not np.isnan(row["ld"]) else 0
        # if row["_id"] == 1342:
        #     print("hello")
        #     pass
        # start -= 1
        # if start < 0:
        #     break
        # print(row)
        # print("*"*20)
        # print(f"hello {row['_id']}")
        df_commit_relations = df_relation[df_relation["_start"] == row["_id"]]
        df_commit_relations = df_commit_relations.append(df_relation[df_relation["_end"] == row["_id"]])
        data_dict["files"] = set()
        data_dict["subsystem"] = set()
        data_dict["directory"] = set()
        data_dict["person"] = set()
        data_dict["comments"] = 0
        data_dict["nrev"] = 0
        data_dict["approver"] = 0
        data_dict["reviewer"] = 0
        data_dict["person_approver"] = 0
        data_dict["person_reviewer"] = 0
        data_dict["person_authored"] = 0
        data_dict["person_commited"] = 0
        data_dict["merged_at"] = 0
        for _, relations in df_commit_relations.iterrows():
            # print(relations[["_start", "_end", "_type"]])
            # print(df_nodes[df_nodes["_id"] == relations["_end"]])
            _nodes = df_nodes[df_nodes["_id"] == relations["_end"]].iloc[0]
            # print(_nodes)

            if _nodes["_labels"] == ":ModFiles":
                data_dict.get("files").add(_nodes["filename"])
                data_dict.get("directory").add(_nodes["directory"])
                data_dict.get("subsystem").add(_nodes["subsystem"])

                data_dict["la"] += int(relations["la_link"]) if not np.isnan(relations["la_link"]) else 0
                data_dict["ld"] += int(relations["ld_link"]) if not np.isnan(relations["ld_link"]) else 0

            elif _nodes["_labels"] == ":PR":
                # TODO: for the pr find the reiewer and merger and then see how the results have changed
                # REVIEWER
                # APPROVER
                # _type
                pr_id = _nodes["_id"]
                df_pr_relations = df_relation[df_relation["_start"] == pr_id]
                df_pr_relations = df_pr_relations.append(df_relation[df_relation["_end"] == pr_id])

                for _, pr_relation in df_pr_relations.iterrows():
                    if pr_relation["_type"] == "REVIEWER":
                        data_dict["reviewer"] += 1
                    if pr_relation["_type"] == "APPROVER":
                        data_dict["approver"] += 1

                data_dict["merged_at"] = _nodes["merged_at"]
                data_dict["comments"] = int(_nodes["comments"])
                data_dict["nrev"] = int(_nodes["nrev"])
            elif _nodes["_labels"] == ":Commit":
                data_dict["parent"] = _nodes["id"]
            elif _nodes["_labels"] == ":Person":
                # TODO: Can add person commits as well, more of the graphs representation

                person_id = _nodes["_id"]
                df_person_relations = df_relation[df_relation["_start"] == person_id]
                df_person_relations = df_person_relations.append(df_relation[df_relation["_end"] == person_id])

                for _, person_relation in df_person_relations.iterrows():
                    if person_relation["_type"] == "REVIEWER":
                        data_dict["person_reviewer"] += 1
                    if person_relation["_type"] == "APPROVER":
                        data_dict["person_approver"] += 1
                    if person_relation["_type"] == "WAS_AUTHORED_BY":
                        data_dict["person_authored"] += 1
                    if person_relation["_type"] == "COMMITED":
                        data_dict["person_commited"] += 1

                data_dict.get("person").add(_nodes["id"])
            elif _nodes["_labels"] == ":Branch":
                pass
            else:
                print(_nodes)
                raise Exception()
        data_dict["no_of_files"] = len(data_dict.get("files"))
        data_dict["no_of_subsystem"] = len(data_dict.get("subsystem"))
        data_dict["no_of_directory"] = len(data_dict.get("directory"))
        data_dict["no_of_person"] = len(data_dict.get("person"))
        if data_dict["merged_at"] is None or data_dict["merged_at"] == "None" or pd.isnull(data_dict["merged_at"]):
            data_dict["merged_at"] = 0
        if data_dict["author_date"] is None or data_dict["author_date"] == "None" or pd.isnull(
                data_dict["author_date"]):
            data_dict["author_date"] = 0
        if data_dict["merged_at"] != 0 and data_dict["author_date"] != 0:
            data_dict["age"] = (parser.parse(data_dict["merged_at"]).replace(tzinfo=None) - parser.parse(
                data_dict["author_date"]).replace(tzinfo=None)).seconds
        else:
            data_dict["age"] = 0
        # print(data_dict)
        # print(f"Time taken for {row['_id']} is {time.time() - start_time} and index is {row.name}")
        return data_dict
