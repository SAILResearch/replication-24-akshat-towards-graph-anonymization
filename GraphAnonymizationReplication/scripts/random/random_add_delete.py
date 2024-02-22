import random
import sys

from pydriller import Repository, Commit
from neo4j import GraphDatabase
from neo4j.exceptions import ConstraintError
from pandas import DataFrame
import datetime
from time import sleep, time
from NodeMaker import NodeMaker
from Utils import Utils
from neo.Neo4jConnection import Neo4jConnection

from github import Github
import pandas as pd
import datetime
from dateutil import parser
from time import sleep
from dateutil import parser
from scripts.anon_utils import utils as anon_utils
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug2.log"),
        logging.StreamHandler()
    ]
)    

if not anon_utils.Utils.is_local_env():
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

nodes_changed = 0
links_changed = 0


def get_nodes_to_delete(mod_files, node_type, new_count, node_maker, node_id, deleting_node_type, main_node):
    global links_changed

    original_count = len(mod_files)
    if new_count > original_count:
        return []

    nodes_to_delete_count = original_count - new_count

    nodes_to_delete = random.sample(mod_files, nodes_to_delete_count)

    for _node_to_delete in nodes_to_delete:
        links_changed += 1
        node_maker.delete_link_of_id(main_node, node_id, deleting_node_type,  _node_to_delete['b']['id'])

    return nodes_to_delete


def add_nodes(node_maker, first_node_id, first_node_type, second_node_type, second_node_link_type,
              mod_file_delete_node_store, new_count, original_count):
    global links_changed
    if original_count > new_count:
        return

    nodes_to_add_count = new_count - original_count
    nodes_to_add_count = min(nodes_to_add_count, len(mod_file_delete_node_store))

    _nodes_to_add = random.sample(mod_file_delete_node_store, nodes_to_add_count)
    for _node_to_add in _nodes_to_add:
        links_changed += 1
        node_maker.link_nodes(first_node_type, first_node_id, second_node_link_type, second_node_type,
                              _node_to_add['b']['id'], _node_to_add['r']['properties'])


def get_random_sample(node_maker, node_type, anonymity_percent):
    total_nodes = node_maker.count_node(node_type)
    number_to_change = int(anonymity_percent * total_nodes / 100)
    print(f"Total people {total_nodes} and random {number_to_change}")

    if node_type != node_maker.COMMIT:
        nodes_to_change = node_maker.find_nodes(node_type, 0, total_nodes)
    else:
        nodes_to_change = node_maker.find_nodes_with_link_unique(node_type, node_maker.LINK_MODIFYIED, 0, total_nodes)

    nodes_to_change = [x['id'] for x in nodes_to_change]

    # make sure this is even
    random_select_commits = random.sample(nodes_to_change, number_to_change)
    if len(random_select_commits) % 2 == 1:
        random_select_commits.append(random.sample(nodes_to_change, 1)[0])

    return random_select_commits


def redistribute_nodes(information_dict):
    existing_node_1 = node_maker.find_node_with_relation(information_dict["main_node_type"],
                                                         information_dict["main_node_id_1"],
                                                         information_dict["modifying_node_link_type"])
    existing_node_2 = node_maker.find_node_with_relation(information_dict["main_node_type"],
                                                         information_dict["main_node_id_2"],
                                                         information_dict["modifying_node_link_type"])

    modded_files_count = len(existing_node_1) + len(existing_node_2)
    new_count_1 = random.randint(0, modded_files_count)
    new_count_2 = modded_files_count - new_count_1

    logging.info(f"id 1 - {information_dict['main_node_id_1']} and id 2 - {information_dict['main_node_id_2']}")
    logging.info(f"old count 1 - {len(existing_node_1)} and old count 2 - {len(existing_node_2)}")
    logging.info(f"new count 1 - {new_count_1} and new count 2 - {new_count_2}")
    
    
    mod_file_delete_node_store = []

    _nodes_to_add = get_nodes_to_delete(existing_node_1, information_dict["modifying_node_type"], new_count_1, node_maker,
                        information_dict["main_node_id_1"], information_dict["modifying_node_link_type"], information_dict["main_node_type"])
    if len(_nodes_to_add) != 0:
        mod_file_delete_node_store.extend(_nodes_to_add)

    _nodes_to_add = get_nodes_to_delete(existing_node_2, information_dict["modifying_node_type"], new_count_2, node_maker,
                        information_dict["main_node_id_2"], information_dict["modifying_node_link_type"], information_dict["main_node_type"])
    if len(_nodes_to_add) != 0:
        mod_file_delete_node_store.extend(_nodes_to_add)

    add_nodes(node_maker, information_dict["main_node_id_1"], information_dict["main_node_type"],
              information_dict["modifying_node_type"], information_dict["modifying_node_link_type"],
              mod_file_delete_node_store, new_count_1, len(existing_node_1))
    add_nodes(node_maker, information_dict["main_node_id_2"], information_dict["main_node_type"],
              information_dict["modifying_node_type"], information_dict["modifying_node_link_type"],
              mod_file_delete_node_store, new_count_2, len(existing_node_2))


if __name__ == '__main__':

    __start_time = time()

    ANONYMITY_PERCENT = 20

    if not anon_utils.Utils.is_local_env():
        ANONYMITY_PERCENT = int(sys.argv[1])

    ANONYMOUS_NODE = [node_maker.COMMIT, node_maker.PERSON]
    LEFT_TO_RIGHT = "left_to_right"
    RIGHT_TO_LEFT = "right_to_left"

    LINK_DEFINITION = {

        node_maker.COMMIT: [
            (node_maker.LINK_MODIFYIED, node_maker.MOD_FILES, LEFT_TO_RIGHT),

            (node_maker.LINK_WAS_AUTHORED_BY, node_maker.PERSON, LEFT_TO_RIGHT),
            # (node_maker.LINK_WRITTEN_BY, node_maker.PERSON, RIGHT_TO_LEFT),
            (node_maker.LINK_COMMITTED, node_maker.PERSON, LEFT_TO_RIGHT),

            (node_maker.LINK_PART_OF, node_maker.PR, LEFT_TO_RIGHT),
        ],

        # write all the links that are present in the graph
        node_maker.PERSON: [
            (node_maker.LINK_WAS_AUTHORED_BY, node_maker.COMMIT, RIGHT_TO_LEFT),
            (node_maker.LINK_COMMITTED, node_maker.COMMIT, LEFT_TO_RIGHT),
            # (node_maker.LINK_WRITTEN_BY, node_maker.COMMIT, LEFT_TO_RIGHT),

            (node_maker.LINK_REVIEWER, node_maker.PR, RIGHT_TO_LEFT),
            (node_maker.LINK_APPROVER, node_maker.PR, RIGHT_TO_LEFT)]
    }


    random_select_commits = get_random_sample(node_maker, node_maker.COMMIT, ANONYMITY_PERCENT)
    logging.info(f"Random commits {len(random_select_commits)}")

    # random_select_commits = ['7b8480744ea6e6fb41efd4329bb470c8f3c763db', '0ab6465a7dece117c61c3efd3ec95d20524bdad6']

    # first delete all nodes
    for i in range(0, len(random_select_commits), 2):
        nodes_changed += 2
        node_id_1 = random_select_commits[i]
        node_id_2 = random_select_commits[i + 1]

        logging.info(f"{i} - {node_id_1} to {node_id_2}")

        info_dict = {
            "main_node_id_1": node_id_1,
            "main_node_id_2": node_id_2,
            "main_node_type": node_maker.COMMIT,
            "modifying_node_link_type": node_maker.LINK_MODIFYIED,
            "modifying_node_type": node_maker.MOD_FILES
        }

        redistribute_nodes(info_dict)

        # take the person node and change the connections they have made



    random_select_person = get_random_sample(node_maker, node_maker.PERSON, ANONYMITY_PERCENT)
    logging.info(f"Random person {len(random_select_person)}")
    # random_select_person = ["chenrui.momo@gmail.com", "yorik.sar@gmail.com"]
    for i in range(0, len(random_select_person), 2):
        nodes_changed += 2
        person_id_1 = random_select_person[i]
        person_id_2 = random_select_person[i + 1]
        
        logging.info(f"{i} - {person_id_1} to {person_id_2}")

        info_dict = {
            "main_node_id_1": person_id_1,
            "main_node_id_2": person_id_2,
            "main_node_type": node_maker.PERSON,
            "modifying_node_type": node_maker.COMMIT,
            "modifying_node_link_type": node_maker.LINK_WAS_AUTHORED_BY
        }

        redistribute_nodes(info_dict)

        info_dict = {
            "main_node_id_1": person_id_1,
            "main_node_id_2": person_id_2,
            "main_node_type": node_maker.PERSON,
            "modifying_node_type": node_maker.PR,
            "modifying_node_link_type": node_maker.LINK_REVIEWER
        }

        redistribute_nodes(info_dict)

        info_dict = {
            "main_node_id_1": person_id_1,
            "main_node_id_2": person_id_2,
            "main_node_type": node_maker.PERSON,
            "modifying_node_type": node_maker.PR,
            "modifying_node_link_type": node_maker.LINK_APPROVER
        }

        redistribute_nodes(info_dict)

    __end_time = time()
    change_data_dict = {
        "nodes_changed" : nodes_changed,
        "links_changed" : links_changed,
        "time_taken" : __end_time - __start_time,
        "date" : datetime.datetime.now(),
        "anonymity_percent" : ANONYMITY_PERCENT
    }

    anon_utils.Utils.save_data_dict(change_data_dict, "random_add_delete_anonymity.csv")


