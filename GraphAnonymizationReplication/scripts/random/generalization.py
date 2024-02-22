import random as random
import time
from collections import defaultdict, OrderedDict
from multiprocessing import Pool
from pydriller import Repository, Commit
from neo4j import GraphDatabase
from neo4j.exceptions import ConstraintError
from pandas import DataFrame
from scripts.anon_utils import utils as anon_utils
import datetime
from time import sleep
from NodeMaker import NodeMaker
from Utils import Utils
from neo.Neo4jConnection import Neo4jConnection
import threading
import concurrent
from pprint import pprint
from github import Github
import pandas as pd
import datetime
from dateutil import parser
from time import sleep
from dateutil import parser
import sys
import os
from scripts.anon_utils.utils import Utils as anon_utils

import logging

from scripts.anon_utils.multiprocess_dict import MultiprocessDict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("threading_true_test.log"),
        logging.StreamHandler()
    ]
)

if not anon_utils.is_local_env():
    conn = Neo4jConnection(uri="bolt://localhost:7687",
                           user="neo4j",
                           pwd="password",
                           db="graph.db")
    parallel_workers = 100
else:
    conn = Neo4jConnection(uri="bolt://localhost:11014",
                           user="neo4j",
                           pwd="password",
                           db="major")
    parallel_workers = 10
node_maker = NodeMaker(conn)

blacklist_nodes = ["jenkins", "smokestack", "trivial-rebase@review.openstack.org"]


def random_person_node_generator():
    pass


def random_commit_node_generator():
    pass


def random_mod_file_node_generator():
    pass


files_dict = MultiprocessDict()

pr_author_dict = MultiprocessDict()
pr_reviewer_dict = MultiprocessDict()

author_experience_dict = MultiprocessDict()

links_changed = 0
nodes_changed = 0


def change_nodes(target_number, current_number, node_id, node_type, link_modified, link_node_type):
    logging.info(
        f"Changing {node_type} {node_id} from {current_number} to {target_number} by adding "
        f"{link_modified} links to {link_node_type}")

    global nodes_changed, links_changed
    nodes_changed += 1

    target_number = int(target_number)
    current_number = int(current_number)

    if target_number > current_number:

        diff = target_number - current_number
        logging.info(f"Adding {diff} links to {node_type} {node_id}")

        # get random nodes of type link_node_type
        link_node_type_total_count = node_maker.count_node(link_node_type)
        random_start = random.randint(0, link_node_type_total_count - diff - 2)
        random_nodes = node_maker.find_nodes(link_node_type, random_start, diff)

        # add link_modified to them
        for random_node in random_nodes:
            relation_dict = None
            if link_modified == node_maker.LINK_MODIFYIED:
                relation_dict = {
                    "la_link": random.randint(0, 200),
                    "ld_link": random.randint(0, 200),
                }
            node_maker.link_nodes(node_type, node_id, link_modified, link_node_type, random_node["id"], relation_dict)
            links_changed += 1


    elif target_number < current_number:
        # remove nodes

        diff = current_number - target_number
        logging.info(f"Removing {diff} links from {node_type} {node_id}")

        # remove these many links from node_id to link_node_type
        current_nodes = node_maker.find_node_with_relation(node_type, node_id, link_modified)

        for i in range(diff):
            if len(current_nodes) == 0:
                break
            node_maker.delete_link_of_id(node_type, node_id, link_modified, current_nodes.pop()["b"]["id"])
            links_changed += 1


def process_commit(commit, limit):
    commit_id = commit["id"]
    commit_info_dict = {}

    limit -= 1
    if limit == 0:
        return

    commit_info = get_commit_info(commit_id)

    return commit_info


def get_commit_info(commit_id):
    # there will be certain limits and according to only them we will
    # be able to do some modifications
    modified_files = node_maker.find_node_with_relation(node_maker.COMMIT, commit_id, node_maker.LINK_MODIFYIED)
    for __file in modified_files:
        __file_name = __file["b"]["id"]
        file_linked_to_commits = files_dict.get_value_and_save(__file_name, node_maker.find_node_with_relation,
                                                               node_maker.MOD_FILES, __file_name,
                                                               node_maker.LINK_MODIFYIED)
        # logging.info(f"File {__file_name} has {len(file_linked_to_commits)} commits")
    # get the pr reviewer and commentor
    # get the pr
    # pr = node_maker.find_node_with_relation(node_maker.COMMIT, commit_id, node_maker.LINK_PART_OF)
    # __pr_approver = []
    # __pr_reviewer = []
    # if len(pr) != 0:
    #     pr = pr[0]["b"]["id"]
    #     __pr_approver = pr_author_dict.get_value_and_save(pr, node_maker.find_node_with_relation,
    #                                                       node_maker.PR, pr, node_maker.LINK_APPROVER)
    #     __pr_reviewer = pr_reviewer_dict.get_value_and_save(pr, node_maker.find_node_with_relation,
    #                                                         node_maker.PR, pr, node_maker.LINK_REVIEWER)
    # else:
    #     pr = None
    # author experience
    commit_author = node_maker.find_node_with_relation(node_maker.COMMIT, commit_id, node_maker.LINK_WAS_AUTHORED_BY)
    author_experience = []
    if len(commit_author) != 0:
        commit_author = commit_author[0]["b"]["id"]
        author_experience = author_experience_dict.get_value_and_save(commit_author, node_maker.find_node_with_relation,
                                                                      node_maker.PERSON, commit_author,
                                                                      node_maker.LINK_WAS_AUTHORED_BY)
    commit_info_dict = {
        "commit_id": commit_id,
        # "pr_id": pr,
        "no_files": len(modified_files),
        # "no_pr_approver": 0,
        # "no_pr_reviewer": 0,
        "author_id": commit_author,
        "author_experience": len(author_experience)
    }
    commit_info_dict["key"] = str(commit_info_dict["no_files"]) + "," \
                              + str(commit_info_dict["author_experience"])
    return commit_info_dict


def shrink_underutilized_clusters(underutilized_clusters):
    santizised_clusters = dict()

    for cluster in underutilized_clusters:
        current_files, current_author_experience = cluster.split(",")

        if int(current_files) > 500:
            continue

        if int(current_author_experience) > 200:
            continue

        # if int(current_pr_reviewer) > 50:
        #     continue

        santizised_clusters[cluster] = underutilized_clusters[cluster]

    return santizised_clusters


if __name__ == "__main__":

    # store the degree of all the nodes, the structure of all the nodes

    # commit, no_files, PR, pr_no_reviewers, pr_no_authors

    k_value = 4
    # cluster_number = 80
    cluster_offset = 30
    __start_time = time.time()

    if not anon_utils.is_local_env():
        k_value = int(sys.argv[1])
        cluster_offset = int(sys.argv[2])
        limit = 1000000000000000000
    else:
        limit = 1000 / parallel_workers

    logging.info(f"K value is {k_value} and cluster number is {cluster_offset}")

    total_number_of_commits = node_maker.count_node(node_maker.COMMIT)
    commit_nodes = node_maker.find_nodes(node_maker.COMMIT, 0, total_number_of_commits)

    structure_dict = dict()

    # make multiple process to loop over the commit nodes
    __process_start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel_workers) as executor:
        future_to_url = {executor.submit(process_commit, commit, limit): commit for commit in commit_nodes}
        for future in concurrent.futures.as_completed(future_to_url):
            commmit_data = future_to_url[future]
            try:
                data_dict = future.result()

                if data_dict["key"] not in structure_dict:
                    structure_dict[data_dict["key"]] = []

                structure_dict.get(data_dict["key"]).append(data_dict)
                # logging.info(f"Data dict is {data_dict}")
            except Exception as exc:
                logging.info(f"{commmit_data} generated an exception: {exc}")
    __process_end_time = time.time()
    logging.info(
        f"Time taken to process {total_number_of_commits} commits is {__process_end_time - __process_start_time}")

    # if True:
    #     for key, value in structure_dict.items():
    #         logging.info(f"Underutilized cluster {key} has {len(value)} commits")
    #     raise

    # sort the structure dict according to the list value

    # ensure there are x clusters where each cluster as y commits

    structure_dict = dict(sorted(structure_dict.items(), key=lambda item: len(item[1])))

    logging.info(f"Total number of clusters is {len(structure_dict.keys())}")
    for key in structure_dict.keys():
        logging.info(f"Key {key} has {len(structure_dict[key])} commits")

    # now that we have a structure dict, we need to make a cluster for each of the key

    surplus_clusters = OrderedDict()
    underutilized_clusters = OrderedDict()

    for key, value in structure_dict.items():

        if len(value) >= k_value:
            surplus_clusters[key] = value
        else:
            underutilized_clusters[key] = value

    full_clusters_count = len(surplus_clusters.keys())

    clusters_to_be_created = cluster_offset
    logging.info(f"Full clusters count is {full_clusters_count} and clusters to be created is {clusters_to_be_created}")
    logging.info(f"Total clusters are {len(structure_dict.keys())}")
    logging.info(f"Surplus clusters are {len(surplus_clusters.keys())}")
    logging.info(f"Underutilized clusters are {len(underutilized_clusters.keys())}")

    # underutilized clusers which are being processed

    if clusters_to_be_created <= 0:
        raise Exception("Not enough clusters to be created")

    # if len(structure_dict) < cluster_number:
    #     raise Exception("Not enough clusters")

    # TODO: Make them so that they are not out of the world

    # logging.info(f"Underutilized clusters are {len(underutilized_clusters.keys())}")
    underutilized_clusters = shrink_underutilized_clusters(underutilized_clusters)
    logging.info(f"sanitized are {len(underutilized_clusters.keys())}")

    processing_clusters = set(random.sample(list(underutilized_clusters.keys()), clusters_to_be_created))

    extra_clusters = set(underutilized_clusters.keys()) - processing_clusters

    # underutilized clusters which are being destroyed

    logging.info(f"Processing clusters are {len(processing_clusters)} extra clusters are {len(extra_clusters)}")
    extra_clusters = list(extra_clusters)

    # if not anon_utils.is_local_env() and sys.argv[3] == "test":
    #     raise Exception("Done")

    for cluster_key in processing_clusters:

        target_files, target_author_experience = cluster_key.split(",")
        cluster_value = underutilized_clusters[cluster_key]

        elements_to_be_added = k_value - len(underutilized_clusters[cluster_key])
        logging.info(f"Elements to be added to cluster {cluster_key} is {elements_to_be_added}")

        while elements_to_be_added > 0:

            # select a random underprocessed cluster
            random_cluster_being_processed = random.choice(extra_clusters)
            current_files, current_author_experience = \
                random_cluster_being_processed.split(",")

            logging.info(f"Current cluster being processed is {random_cluster_being_processed}")

            for random_element in underutilized_clusters[random_cluster_being_processed]:
                elements_to_be_added -= 1

                # change files of this
                change_nodes(target_files, current_files, random_element["commit_id"], node_maker.COMMIT,
                             node_maker.LINK_MODIFYIED, node_maker.MOD_FILES)

                if random_element["author_id"] is not None:
                    # TODO get pr ID
                    change_nodes(target_author_experience, current_author_experience, random_element["author_id"], node_maker.PERSON,
                                 node_maker.LINK_WAS_AUTHORED_BY, node_maker.COMMIT)

                # TODO: get author ID
                # change_nodes(target_author_experience, target_author_experience, )

            # "no_files": len(modified_files),
            # "no_pr_approver": len(__pr_approver),
            # "no_pr_reviewer": len(__pr_reviewer),
            # "author_experience": len(author_experience)

    # for key, value in underutilized_clusters.items():
    #     logging.info(f"Underutilized cluster {key} has {len(value)} commits")

    __end_time = time.time()
    change_info_dict = {
        "clusters": cluster_offset,
        "k_value": k_value,
        "nodes_changed": nodes_changed,
        "links_changed": links_changed,
        "time": __end_time - __start_time,
        "current_time": datetime.datetime.now()
    }

    __file_name = "generatlisation.csv"
    anon_utils.save_data_dict(change_info_dict, __file_name)

    # chose a surplus cluster which has more than k_value commits

    # for each under, do something

    # i want to have 100 clusters which have over 3 entities

    # find cluseters which are under 3 and count of such that is less than 100

    # then then randomly from them choose clusters and join them and make links and make htings work
