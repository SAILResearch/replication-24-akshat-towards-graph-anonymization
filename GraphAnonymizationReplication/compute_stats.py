import concurrent
import datetime
import logging
import math
import os
import sys
import threading
import time
from multiprocessing import Pool

import pandas as pd
from dateutil import parser

from NodeMaker import NodeMaker
from neo.Neo4jConnection import Neo4jConnection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug5.log"),
        logging.StreamHandler()
    ]
)

g_file_name = None

node_make_dict_lock = threading.Lock()
count_lock = threading.Lock()
save_dict_lock = threading.Lock()

print_block_time = False
dummy_run = False

global_count = 0
f_limit = 500

file_metrics_dict = {}

author_relative_experience_dict = {}

reviewer_relative_experience_dict = {}

reviewer_substem_experience_dict = {}

author_subsyem_experience_dict = {}

# all dicts to cache data
person_file_dict = {}

cache_person_reviewer_pr_dict = {}

smart_nuc_ndev_dict = {}

author_awareness_dict = {}

file_unique_author_dict = {}

file_unique_commit_dict = {}

# node_maker.COMMIT, data_dict["commit_id"], node_maker.LINK_MODIFYIED
cache_commit_modified_file_dict = {}

# node_maker.MOD_FILES, __file_name, node_maker.LINK_MODIFYIED
cache_file_modified_commit_dict = {}

# node_maker.COMMIT, mod_commits["b"]["id"], node_maker.LINK_WAS_AUTHORED_BY
cache_commit_author_person_dict = {}

# TODO: optimize this to just have length
# node_maker.PERSON, pull_author, node_maker.LINK_WAS_AUTHORED_BY
cache_person_author_commit_dict = {}

# node_maker.PERSON, pull_author, node_maker.LINK_REVIEWER
cache_person_reviewer_commit_dict = {}

# node_maker.PR, pull_request['id'], node_maker.LINK_REVIEWER
cache_pr_reviewer_commit_dict = {}

# node_maker.PR, pull_request['id'], node_maker.LINK_APPROVER
cache_pr_approver_commit_dict = {}

# node_maker.PR, __pr['b']['id'], node_maker.LINK_PART_OF
cache_pr_partof_commit_dict = {}

locker_dict = {}
locker_key_lock = threading.Lock()

cache_find = 0
cache_find_after_wait = 0
cache_not_find = 0

time_lock_key_wait = 0
time_wait_for_specific_key = 0
time_calc_results = 0


def get_item_from_cache_and_save(cache_dict, key, count, func, *args):
    global time_lock_key_wait, time_wait_for_specific_key, time_calc_results, cache_find, cache_find_after_wait, cache_not_find

    key_name = f"{key}_{args[0]}_{args[2]}"
    # key_name = key

    if key_name in cache_dict.keys():
        cache_find += 1
        # if print_block_time: logging.info(f"count - {count} lock found in cache: {key_name}")
        return cache_dict[key_name]

    __time_lock_key_wait = time.time()
    # if print_block_time: logging.info(f"count - {count} lock getting lock for key {key_name}")
    __lock_wait_start_time = time.time()
    # with locker_key_lock:
    # if print_block_time: logging.info(f"count - {count} lock locker_key_lock wait time: "
    #   f"{time.time() - __lock_wait_start_time}")
    specific_key_locker = locker_dict.get(key_name, threading.Lock())
    locker_dict[key_name] = specific_key_locker
    time_lock_key_wait += time.time() - __time_lock_key_wait

    __time_wait_for_specific_key = time.time()
    with specific_key_locker:
        time_wait_for_specific_key += time.time() - __time_wait_for_specific_key
        # if print_block_time: logging.info(
        # f"count - {count} lock specific_key_locker wait time: {time.time() - __time_wait_for_specific_key}")
        if key_name in cache_dict.keys():
            cache_find_after_wait += 1
            # if print_block_time: logging.info(f"count - {count} lock after locker found in cache: {key_name}")
            return cache_dict[key_name]
        __calc_start_time = time.time()
        cache_not_find += 1
        cache_dict[key_name] = func(args[0], args[1], args[2])
        # if print_block_time: logging.info(
        # f"count - {count} lock calculated locker Time taken to item: {time.time() - __calc_start_time}")
        time_calc_results += time.time() - __calc_start_time
        return cache_dict[key_name]


def compute_stats_for_commit(commit, node_maker, df_reference, total_number_of_commits):
    global global_count
    global f_limit

    print_block_time = os.getenv("PRINT_BLOCK_TIME", "True") == "True"

    with count_lock:
        f_limit -= 1
        if f_limit < 0 and dummy_run:
            return

    with count_lock:
        global_count += 1
        count = global_count

    logging.info("*" * 100)
    logging.info(f"count - {count} / {total_number_of_commits} percent done "
                 f"{(100 * count) / total_number_of_commits} commit: {commit['id']}")
    __commit_start_time = time.time()

    row_reference = df_reference[df_reference["commit_id"] == commit["id"]]
    if len(row_reference) == 0:
        logging.info(f"count - {count} - Commit not in reference, continuing")
        return

    data_dict = {}
    data_dict["commit_id"] = commit["id"]
    data_dict["tcmt"] = 0

    # get the bug count and fix count
    for __key in ["bugcount", "fixcount"]:
        if pd.isna(row_reference[__key]).all() or int(row_reference[__key]) == 0:
            data_dict[__key] = 0
        else:
            data_dict[__key] = 1

    # this should not be happenning now
    if "author_date" not in commit.keys():
        logging.info(f"count - {count} - Ignoring commit as there is no author date")
        return

    data_dict["author_date"] = commit["author_date"]

    unique_file_list, unique_subsystem_list = get_la_ld_metrics(print_block_time, count, data_dict, node_maker,
                                                                total_number_of_commits)

    # pull_author, pull_reviewers_list = get_pr_metrics(count, data_dict, node_maker)
    try:
        # TODO: verify if this is correct
        pull_author = get_item_from_cache_and_save(cache_commit_author_person_dict, data_dict["commit_id"], count,
                                                   node_maker.find_node_with_relation, node_maker.COMMIT,
                                                   data_dict["commit_id"], node_maker.LINK_WAS_AUTHORED_BY)[0]["b"]["id"]
        # pull_author = node_maker.find_node_with_relation(node_maker.COMMIT, data_dict["commit_id"], node_maker.LINK_WAS_AUTHORED_BY)[0]["b"]["id"]
    except Exception:
        logging.info(f"count - {count} There should be one author! Error finding author for pull request - {data_dict['commit_id']}")
        pull_author = None

    get_nuc_ndev(print_block_time, count, data_dict, node_maker, unique_file_list)

    get_age(data_dict, node_maker, count, unique_file_list)

    authors_experience = get_aexp(count, data_dict, node_maker, pull_author)

    # all_reviewers = get_rexp(print_block_time, count, data_dict, node_maker, pull_reviewers_list)

    current_commit_date = get_arexp(authors_experience, count, data_dict, pull_author)

    # get_rrexp(print_block_time, all_reviewers, count, current_commit_date, data_dict, node_maker)

    get_asexp(unique_subsystem_list, print_block_time, authors_experience, count, data_dict, node_maker)

    # get_rsexp(unique_subsystem_list, print_block_time, all_reviewers, count, data_dict, node_maker)

    __commit_end_time = time.time()

    logging.info(f"count - {count} - time taken {__commit_end_time - __commit_start_time}")

    logging.info(f"count - {count} - data_dict - {data_dict}")

    return data_dict


def get_rsexp(unique_subsystem_list, print_block_time, all_reviewers, count, data_dict, node_maker):

    """
    This function calculates the reviewer subsystem experience
    """

    __block_start_time = time.time()
    reviewers_subsystem_experience = list()
    reviewers_subsystem_experience_count = 0

    for __pr_reviewer in all_reviewers.keys():
        __loop_start_time = time.time()
        if __pr_reviewer not in reviewer_substem_experience_dict.keys():
            __reviewer_subsytem_experience_dict_specific = list()

            if print_block_time: logging.info(
                f"count - {count} - detail Processing {__pr_reviewer} subsystem experience")

            __commits = get_item_from_cache_and_save(cache_person_author_commit_dict, __pr_reviewer, count,
                                                     node_maker.find_node_with_relation, node_maker.PERSON,
                                                     __pr_reviewer, node_maker.LINK_WAS_AUTHORED_BY)

            # commit experience
            for __commit in __commits:
                __files = get_item_from_cache_and_save(cache_commit_modified_file_dict, __commit["b"]["id"], count,
                                                       node_maker.find_node_with_relation, node_maker.COMMIT,
                                                       __commit["b"]["id"], node_maker.LINK_MODIFYIED)
                for __file in __files:
                    reviewers_subsystem_experience.append(__file["b"]["subsystem"])
                    __reviewer_subsytem_experience_dict_specific.append(__file["b"]["subsystem"])
            reviewer_substem_experience_dict[__pr_reviewer] = __reviewer_subsytem_experience_dict_specific

        else:

            if print_block_time: logging.info(
                f"count - {count} - {__pr_reviewer} detail subsystem experience already calculated")
            reviewers_subsystem_experience.extend(reviewer_substem_experience_dict[__pr_reviewer])

        __loop_end_time = time.time()
        if print_block_time: logging.info(
            f"count - {count} - detail loop Processing {__pr_reviewer} subsystem experience time taken {__loop_end_time - __loop_start_time}")

    for __subsystem in unique_subsystem_list:
        reviewers_subsystem_experience_count += reviewers_subsystem_experience.count(__subsystem)

    data_dict["rsexp"] = reviewers_subsystem_experience_count
    data_dict["osexp"] = data_dict["rsexp"] + data_dict["asexp"]

    logging.info(f"count - {count} - Processing {len(all_reviewers)} reviewers subsystem experience "
                 f"Time taken to calculate reviewer subsystem experience metrics: {time.time() - __block_start_time}")


def get_asexp(unique_subsystem_list, print_block_time, authors_experience, count, data_dict, node_maker):

    __block_start_time = time.time()

    author_set_of_subsystem_experience = 0

    author_set_of_subsystem = list()

    if len(authors_experience) == 0:
        data_dict["asexp"] = len(author_set_of_subsystem)
        return

    for __commit in authors_experience:
        __author_experient_loop_start = time.time()

        if __commit["b"]["id"] not in author_subsyem_experience_dict.keys():

            if print_block_time: logging.info(
                f"count - {count} - detail author experience Processing commit - {__commit['b']['id']}")
            __files = get_item_from_cache_and_save(cache_commit_modified_file_dict, __commit["b"]["id"], count,
                                                   node_maker.find_node_with_relation, node_maker.COMMIT,
                                                   __commit["b"]["id"], node_maker.LINK_MODIFYIED)
            for __file in __files:
                author_set_of_subsystem.append(__file["b"]["subsystem"])

            author_subsyem_experience_dict[__commit["b"]["id"]] = author_set_of_subsystem
        else:
            if print_block_time: logging.info(
                f"count - {count} - detail already calculated author experience commit - {__commit['b']['id']} ")
            author_set_of_subsystem = author_subsyem_experience_dict[__commit["b"]["id"]]

        __author_experience_loop_end = time.time()
        if print_block_time: logging.info(
            f"count - {count} - detail loop author experience loop time - {__author_experience_loop_end - __author_experient_loop_start}")

    for __subsystem in unique_subsystem_list:
        author_set_of_subsystem_experience += author_set_of_subsystem.count(__subsystem)

    data_dict["asexp"] = author_set_of_subsystem_experience

    logging.info(f"count - {count} - Processing {len(authors_experience)} authors subsystem experience"
                 f"Time taken to calculate author subsystem experience metrics: {time.time() - __block_start_time}")


def get_rrexp(print_block_time, all_reviewers, count, current_commit_date, data_dict, node_maker):
    # global reviewer_relative_experience_dict

    __block_start_time = time.time()
    reviewer_relative_experience = 0
    __reviewer_experience_dict = {}

    __review_calculated_for = 0
    # logging.info(f"{all_reviewers.keys()}")
    for __pr_reviewer in all_reviewers.keys():

        if __pr_reviewer not in reviewer_relative_experience_dict:

            # logging.info(f"{reviewer_relative_experience_dict.keys()}")
            # logging.info(f"{__pr_reviewer} not in reviewer_relative_experience_dict")
            __review_calculated_for += 1

            __reviewer_relative_experience_start_time = time.time()

            __commits = get_item_from_cache_and_save(cache_person_author_commit_dict, __pr_reviewer, count,
                                                     node_maker.find_node_with_relation,
                                                     node_maker.PERSON, __pr_reviewer, node_maker.LINK_WAS_AUTHORED_BY)
            __saving_reviewer_dict = {}
            for __commit in __commits:
                __reviewer_relative_experience_pr_start_time = time.time()
                if "author_date" not in __commit["b"].keys():
                    if print_block_time: logging.info(
                        f" count - {count} author date not in commit for author experience")
                    continue

                __reviewer_experience_commit_date = parser.parse(__commit["b"]["author_date"], ignoretz=True)
                __year_commit_was_created = __reviewer_experience_commit_date.year
                __saving_reviewer_dict[__year_commit_was_created] = __saving_reviewer_dict.get(
                    __year_commit_was_created, 0) + 1

                # __year = current_commit_date.year - __reviewer_experience_commit_date.year
                # __reviewer_experience_dict[__year] = __reviewer_experience_dict.get(__year, 0) + 1

                # __saving_reviewer_dict[__year] = __saving_reviewer_dict.get(__year, 0) + 1

                __reviewer_relative_experience_pr_end_time = time.time()

                if print_block_time:  logging.info(
                    f"count - {count} - detail loop Time taken to calculate reviewer relative"
                    f" experience metrics for a PR {__pr_reviewer}"
                    f": {__reviewer_relative_experience_pr_end_time - __reviewer_relative_experience_pr_start_time}")

            __reviewer_relative_experience_end_time = time.time()

            reviewer_relative_experience_dict[__pr_reviewer] = __saving_reviewer_dict

            if print_block_time: logging.info(
                f"count - {count} - detail loop Time taken to calculate reviewer relative experience   {__pr_reviewer}"
                f"metrics for a reviewer: {__reviewer_relative_experience_end_time - __reviewer_relative_experience_start_time}")

    for __pr_reviewer in all_reviewers.keys():
        for __year_commit in reviewer_relative_experience_dict[__pr_reviewer].keys():
            __year_dif = current_commit_date.year - __year_commit
            __reviewer_experience_dict[__year_dif] = __reviewer_experience_dict.get(__year_dif, 0) + \
                                                     reviewer_relative_experience_dict[__pr_reviewer][__year_commit]

    # TODO: verify this
    for __key, __value in __reviewer_experience_dict.items():
        if __key >= 0:
            reviewer_relative_experience += (__value / (1 + __key))

    data_dict["rrexp"] = reviewer_relative_experience
    data_dict["orexp"] = data_dict.get("arexp", 0) + data_dict.get("rrexp", 0)

    logging.info(f"count - {count} -  Processing {len(all_reviewers)} reviewers experience"
                 f"Time taken to calculate reviewer"
                 f" relative experience metrics: {time.time() - __block_start_time}"
                 f"reviewer relative experience calculated for {__review_calculated_for} / {len(all_reviewers)} reviewers")


def get_arexp(authors_experience, count, data_dict, pull_author):
    __block_start_time = time.time()
    author_relative_experience = 0
    current_commit_date = parser.parse(data_dict["author_date"], ignoretz=True)

    if len(authors_experience) == 0:
        data_dict["arexp"] = author_relative_experience
        return current_commit_date

    __author_experience_dict = {}

    for __author_experience_commit in authors_experience:

        if "author_date" not in __author_experience_commit["b"].keys():
            if print_block_time: logging.info(f" count - {count} author date not in commit for author experience")
            continue

        # TODO: see if the dates and dict gets created correctly
        __author_experience_commit_date = parser.parse(__author_experience_commit["b"]["author_date"], ignoretz=True)
        __year = current_commit_date.year - __author_experience_commit_date.year
        __author_experience_dict[__year] = __author_experience_dict.get(__year, 0) + 1

    for __key, __value in __author_experience_dict.items():
        if __key >= 0:
            author_relative_experience += (__value / (1 + __key))

    data_dict["arexp"] = author_relative_experience

    logging.info(f"count - {count} - Processing {len(authors_experience)} authors experience Time taken to calculate"
                 f" author experience metrics: {time.time() - __block_start_time}")
    return current_commit_date


def get_rexp(print_block_time, count, data_dict, node_maker, pull_reviewers_list):
    __block_start_time = time.time()
    # reviewer commits and experience
    reviewer_commit_totals = 0
    all_reviewers = dict()
    if len(pull_reviewers_list) != 0:
        for __pr_reviewer in pull_reviewers_list:
            __reviewer_name = __pr_reviewer["b"]["id"]

            reviewers_experience = get_item_from_cache_and_save(cache_person_author_commit_dict, __reviewer_name, count,
                                                                node_maker.find_node_with_relation, node_maker.PERSON,
                                                                __reviewer_name, node_maker.LINK_WAS_AUTHORED_BY)

            # TODO: I dont think we use the value of this dict, just use the keys
            all_reviewers[__reviewer_name] = reviewers_experience
            reviewer_commit_totals += len(reviewers_experience)
    data_dict["rexp"] = reviewer_commit_totals
    data_dict["oexp"] = data_dict.get("aexp", 0) + data_dict.get("rexp", 0)
    if print_block_time: logging.info(
        f"count - {count} - Time taken to calculate reviewer experience metrics:  {time.time() - __block_start_time}" \
        f"and total reviewers {len(pull_reviewers_list)}")
    return all_reviewers


def get_aexp(count, data_dict, node_maker, pull_author):
    __block_start_time = time.time()
    # author commits and experience
    authors_experience = []
    if pull_author != None:
        authors_experience = get_item_from_cache_and_save(cache_person_author_commit_dict, pull_author, count,
                                                          node_maker.find_node_with_relation, node_maker.PERSON,
                                                          pull_author, node_maker.LINK_WAS_AUTHORED_BY)
    data_dict["aexp"] = len(authors_experience)
    logging.info(f"count - {count} - author experience aexp: {time.time() - __block_start_time}")
    return authors_experience


def get_age(data_dict, node_maker, count, unique_file_list):
    if len(unique_file_list) == 0:
        data_dict["age"] = 0
        return

    file_mod_commit_dict = {}
    for file in unique_file_list:
        file_changing_commits = get_item_from_cache_and_save(cache_file_modified_commit_dict, file, count,
                                                             node_maker.find_node_with_relation,
                                                             node_maker.MOD_FILES,
                                                             file, node_maker.LINK_MODIFYIED)
        file_mod_commit_dict[file] = file_changing_commits

    current_date = parser.parse(data_dict["author_date"], ignoretz=True)

    age = 0
    count = 0
    for key, value in file_mod_commit_dict.items():
        max_commit_date = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=None )
        for commit in value:
            if "author_date" in commit["b"].keys():
                commit_date = parser.parse(commit["b"]["author_date"], ignoretz=True)

                if max_commit_date < commit_date < current_date:
                    max_commit_date = commit_date

        count += 1
        age += (current_date - max_commit_date).seconds

    data_dict["age"] = age / count if count != 0 else 0

    #
    #
    # # not caching this as it is not used anywhere else
    # parent_commit = node_maker.find_node_with_relation(node_maker.COMMIT, data_dict["commit_id"],
    #                                                    node_maker.LINK_PARENT)
    # data_dict["age"] = 0
    # if len(parent_commit) != 0 and "author_date" in parent_commit[0]['b'].keys():
    #     data_dict["age"] = (
    #             parser.parse(data_dict["author_date"]) - parser.parse(parent_commit[0]['b']['author_date'])).seconds


def get_nuc_ndev(print_block_time, count, data_dict, node_maker, unique_file_list):
    __block_start_time = time.time()
    total_number_of_devs = 0
    file_total_number_of_commits = 0
    __file_block_start_time = time.time()

    __current_commit_date = parser.parse(data_dict["author_date"], ignoretz=True)

    for file in unique_file_list:

        if file not in file_unique_author_dict.keys():

            if print_block_time: logging.info(f"count - {count} - detail Processing file nuc and ndev - {file}")

            file_changing_commits = get_item_from_cache_and_save(cache_file_modified_commit_dict, file, count,
                                                                 node_maker.find_node_with_relation,
                                                                 node_maker.MOD_FILES,
                                                                 file, node_maker.LINK_MODIFYIED)

            unique_authors = set()
            for mod_commits in file_changing_commits:

                authors = get_item_from_cache_and_save(cache_commit_author_person_dict, mod_commits["b"]["id"], count,
                                                       node_maker.find_node_with_relation, node_maker.COMMIT,
                                                       mod_commits["b"]["id"], node_maker.LINK_WAS_AUTHORED_BY)
                for authored in authors:
                    unique_authors.add(authored["b"]["id"])

                __commit_mod_dict = {"commit": mod_commits, "authors": unique_authors}
                if file not in smart_nuc_ndev_dict.keys():
                    smart_nuc_ndev_dict[file] = []
                smart_nuc_ndev_dict[file].append(__commit_mod_dict)

            # cahce the number of commits and number of authors
            file_total_number_of_commits += len(file_changing_commits)
            file_unique_commit_dict[file] = file_changing_commits

            total_number_of_devs += len(unique_authors)
            file_unique_author_dict[file] = unique_authors
        else:
            if print_block_time: logging.info(f"count - {count} - detail found nuc and ndev - {file}")
            total_number_of_devs += len(file_unique_author_dict[file])
            file_total_number_of_commits += len(file_unique_commit_dict[file])

    new_nuc = set()
    new_ndev = set()

    for file in unique_file_list:

        if file not in smart_nuc_ndev_dict.keys():
            raise Exception("FILE SHOULD BE IN SMART NUC NDEV DICT")

        for __commit_info_dict in smart_nuc_ndev_dict[file]:
            if __current_commit_date > parser.parse(__commit_info_dict["commit"]["b"]["author_date"], ignoretz=True ):
                new_nuc.add(__commit_info_dict["commit"]["b"]["id"])
                new_ndev = new_ndev.union(__commit_info_dict["authors"])

    logging.info(
        f"count - {count} - detail new nuc and ndev - {len(new_nuc)} - {len(new_ndev)} old - {file_total_number_of_commits} - {total_number_of_devs}")
    data_dict["nuc"] = len(new_nuc)
    data_dict["ndev"] = len(new_ndev)
    # data_dict["nuc"] = file_total_number_of_commits
    # data_dict["ndev"] = total_number_of_devs
    __file_block_end_time = time.time()
    logging.info(
        f"count - {count} - Processing {len(unique_file_list)} files with time {__file_block_end_time - __file_block_start_time}")


def get_pr_metrics(count, data_dict, node_maker):
    __block_start_time = time.time()
    # setting default values for pull request related metrics
    data_dict['app'] = 0
    data_dict['rtime'] = 0
    data_dict['self'] = False
    data_dict['hcmt'] = 0
    data_dict["nrev"] = 0
    # not caching this as it is not used anywhere else
    pulls = node_maker.find_node_with_relation(node_maker.COMMIT, data_dict["commit_id"], node_maker.LINK_PART_OF)
    pull_reviewers_list = []
    pull_author = None
    # ideally every commit is part of one pull request
    pull_approver_list = []
    __self_approved_by = False


    try:
        # TODO: verify if this is correct
        pull_author = get_item_from_cache_and_save(cache_commit_author_person_dict, data_dict["commit_id"], count,
                                                   node_maker.find_node_with_relation, node_maker.COMMIT,
                                                   data_dict["commit_id"], node_maker.LINK_WAS_AUTHORED_BY)[0]["b"]["id"]
        # pull_author = node_maker.find_node_with_relation(node_maker.COMMIT, data_dict["commit_id"], node_maker.LINK_WAS_AUTHORED_BY)[0]["b"]["id"]
    except Exception:
        logging.info("There should be one author! Error finding author for pull request - ", data_dict["commit_id"])
        pull_author = None


    if len(pulls) != 0:
        # extract the pull request
        pull_request = pulls[0]["b"]

        # TODO: verify if both the results are the same
        # find the reviewers and approvers
        pull_reviewers_list = get_item_from_cache_and_save(cache_pr_reviewer_commit_dict, pull_request['id'], count,
                                                           node_maker.find_node_with_relation, node_maker.PR,
                                                           pull_request['id'], node_maker.LINK_REVIEWER)
        pull_approver_list = get_item_from_cache_and_save(cache_pr_approver_commit_dict, pull_request['id'], count,
                                                          node_maker.find_node_with_relation, node_maker.PR,
                                                          pull_request['id'],
                                                          node_maker.LINK_APPROVER)

        # pull_reviewers_list = node_maker.find_node_with_relation(node_maker.PR, pull_request['id'], node_maker.LINK_REVIEWER)
        # pull_approver_list = node_maker.find_node_with_relation(node_maker.PR, pull_request['id'], node_maker.LINK_APPROVER)

        # TODO: see why the review time is not being calculated correctly, it is small
        if pull_request["approval_date"] not in ['None', None] and pull_request["created_at"] not in ['None', None]:
            __review_time = (
                    parser.parse(pull_request["approval_date"], ignoretz=True) - parser.parse(pull_request["created_at"], ignoretz=True)).seconds
        else:
            __review_time = 0

        # find author for the pull request
        if pull_request["approval_date"] not in ['None', None] and pull_author is not None:
            # TODO: verify this
            for __approver in pull_approver_list:
                if __approver['b']['id'] == pull_author:
                    __self_approved_by = True
                    break



        data_dict['app'] = len(pull_reviewers_list) + len(pull_approver_list)
        data_dict['hcmt'] = pull_request["comments"]
        data_dict["nrev"] = pull_request["nrev"]
        data_dict['rtime'] = __review_time




    data_dict['self'] = __self_approved_by
    data_dict["revd"] = not data_dict["self"]
    logging.info(f"count - {count} - Time taken to calculate pull request metrics: {time.time() - __block_start_time}")
    return pull_author, pull_reviewers_list


def get_la_ld_metrics(print_block_time, count, data_dict, node_maker, total_number_of_commits):
    __block_start_time = time.time()

    commit_file_list = get_item_from_cache_and_save(cache_commit_modified_file_dict, data_dict["commit_id"], count,
                                                    node_maker.find_node_with_relation,
                                                    node_maker.COMMIT, data_dict["commit_id"],
                                                    node_maker.LINK_MODIFYIED)
    unique_file_list = set()
    unique_directory_list = set()
    unique_subsystem_list = set()
    data_dict["la"] = 0
    data_dict["ld"] = 0

    __file_level_churn = {}
    __total_churn = 0
    for item in commit_file_list:
        __file_name = item["b"]['new_path']

        # if __file_name not in file_metrics_dict.keys():

        if print_block_time: logging.info(f"count - {count} - detail File not in file_metrics_dict: {__file_name}")

        unique_file_list.add(__file_name)
        unique_directory_list.add(item["b"]['directory'])
        unique_subsystem_list.add(item["b"]['subsystem'])

        data_dict["la"] += int(item['r']["properties"]["la_link"])
        data_dict["ld"] += int(item['r']["properties"]["ld_link"])

        # __file_level_churn[__file_name] = int(item['r']["properties"]["la_link"]) + int(item['r']["properties"]["ld_link"])
        __file_level_churn[__file_name] = int(item['r']["properties"]["la_link"])
        __total_churn += __file_level_churn[__file_name]

    # data_dict["ent"] = - sum([p * math.log(p, 2) for p in entropy_list if p != 0])
    entropy_list = []
    for __churn_file in __file_level_churn.keys():
        entropy_list.append(0 if __total_churn == 0 else __file_level_churn[__churn_file] / __total_churn)
    data_dict["ent"] = sum([-1 * p * math.log(p, 2) for p in entropy_list if p != 0])

    # find the commits modifying the file
    # __number_of_commits = get_item_from_cache_and_save(cache_file_modified_commit_dict, __file_name, count,
    #                                                    node_maker.find_node_with_relation, node_maker.MOD_FILES,
    #                                                    __file_name, node_maker.LINK_MODIFYIED)
    # entropy_list.append(len(__number_of_commits) / total_number_of_commits)

    # file_metrics_dict[__file_name] = (
    #     __file_name,
    #     item["b"]['directory'],
    #     item["b"]['subsystem'],
    #     int(item['r']["properties"]["la_link"]),
    #     int(item['r']["properties"]["ld_link"]),
    #     len(__number_of_commits)
    # )
    # else:
    #     if print_block_time: logging.info(f"count - {count} - detail File in file_metrics_dict: {__file_name}")
    #     a, b, c, d, e, f = file_metrics_dict[__file_name]
    #     unique_file_list.add(a)
    #     unique_directory_list.add(b)
    #     unique_subsystem_list.add(c)
    #     data_dict["la"] += int(d)
    #     data_dict["ld"] += int(e)
    #     entropy_list.append(f / total_number_of_commits)

    # calculate metrics

    data_dict["churn"] = data_dict["la"] + data_dict["ld"]
    data_dict["nf"] = len(unique_file_list)
    data_dict["nd"] = len(unique_directory_list)
    data_dict["ns"] = len(unique_subsystem_list)
    # data_dict["ent"] = - sum([p * math.log(p, 2) for p in entropy_list if p != 0])

    logging.info(f"count - {count} - Time taken to calculate file metrics: {time.time() - __block_start_time} \
        and files: {len(commit_file_list)}")

    return unique_file_list, unique_subsystem_list


# TODO: add prints in between to see what is happening
if __name__ == '__main__':
    if os.environ.get('run_env', 'prod') == 'prod':
        conn = Neo4jConnection(uri="bolt://localhost:7687",
                               user="neo4j",
                               pwd="password",
                               db="graph.db")
        parallel_workers = 300
    else:
        conn = Neo4jConnection(uri="bolt://localhost:11014",
                               user="neo4j",
                               pwd="password",
                               db="major")
        parallel_workers = 10
    node_maker = NodeMaker(conn)

    # get the file prefix

    if len(sys.argv) < 2:
        file_prefix = "test"
        file_name = "apachejit_total"
    else:
        file_prefix = str(sys.argv[1])
        file_name = str(sys.argv[2])

    g_file_name = file_name


    logging.info(f"{file_prefix} - {file_name} ")
    __total_start_time = time.time()

    # limit of the number of commits to be processed
    start = 0
    jump = 600
    limit = 100000000
    end = start + limit

    sleep_delay = 0

    # find the total number of commits
    total_number_of_commits = node_maker.count_node(node_maker.COMMIT)

    commit_nodes = node_maker.find_nodes(node_maker.COMMIT, start, jump)

    # df is the final dataframe
    df = pd.DataFrame()
    # df_reference is the dataframe for bugs and not bugs
    df_reference = pd.read_csv(f"{file_name}.csv")

    # loop while there are commits to process
    while len(commit_nodes) != 0:

        if f_limit < 0 and dummy_run:
            # logging.info("skipping run cause dummy")
            break

        logging.info("^" * 100)
        logging.info(f"start - {start} jump - {jump}")
        commit_nodes = node_maker.find_nodes(node_maker.COMMIT, start, jump)
        start += jump

        __commit_batch_start_time = time.time()

        # process each commit
        # for commit in commit_nodes:

        #     data_dict = compute_stats_for_commit(commit, node_maker, df_reference)


        with concurrent.futures.ThreadPoolExecutor(parallel_workers) as executor:
            future_to_commit = {executor.submit(compute_stats_for_commit, commit, node_maker, df_reference,
                                                total_number_of_commits): commit for commit in commit_nodes}
            for future in concurrent.futures.as_completed(future_to_commit):
                commit = future_to_commit[future]
                try:
                    data_dict = future.result()
                    if data_dict is not None and len(data_dict) > 3:
                        df = pd.concat([df, pd.DataFrame([data_dict])], ignore_index=True)
                except Exception as exc:
                    logging.info(f"####################################################################")
                    logging.info(f"####################################################################")
                    logging.info(f"####################################################################")
                    logging.info(f"{commit} generated an exception: {exc} stack trace {exc.__traceback__}")
                    logging.info(f"####################################################################")
                    logging.info(f"####################################################################")
                    logging.info(f"####################################################################")

        __commit_batch_end_time = time.time()
        logging.info(f"start {start} - Time for batch - {__commit_batch_end_time - __commit_batch_start_time}")

    __total_end_time = time.time()
    logging.info(f"Total time taken {__total_end_time - __total_start_time}")
    totoal_cache_calls = cache_find + cache_find_after_wait + cache_not_find
    if totoal_cache_calls == 0: totoal_cache_calls = 1
    logging.info(
        f"Cache statistics - cache_find - {cache_find} cache_find_after_wait - {cache_find_after_wait} cache_not_find - {cache_not_find}")
    logging.info(
        f"Cache statistics - totoal_cache_calls - {totoal_cache_calls} cache_find_percentage - {cache_find / totoal_cache_calls} cache_find_after_wait_percentage - {cache_find_after_wait / totoal_cache_calls} cache_not_find_percentage - {cache_not_find / totoal_cache_calls}")
    logging.info(
        f"Cache statistics - time_lock_key_wait - {time_lock_key_wait} time_wait_for_specific_key - {time_wait_for_specific_key} time_calc_results - {time_calc_results}")

    df["tcmt"] = 0
    logging.info(f"fix_count - {df['fixcount'].sum()}  bug_count - {df['bugcount'].sum()}")

    df["author_date"] = df["author_date"].apply(lambda x: int(parser.parse(x).timestamp() if pd.notna(x) else 0))

    file_name = f"{file_prefix}-{datetime.datetime.now()}.csv"
    logging.info(file_name)
    df.to_csv(file_name)
