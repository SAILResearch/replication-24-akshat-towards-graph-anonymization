import random as random
import time

from pydriller import Repository, Commit
from neo4j import GraphDatabase
from neo4j.exceptions import ConstraintError
from pandas import DataFrame
import datetime
from time import sleep
from NodeMaker import NodeMaker
from Utils import Utils
from neo.Neo4jConnection import Neo4jConnection

from scripts.anon_utils import utils as anon_utils
from pprint import pprint
from github import Github
import pandas as pd
import datetime
from dateutil import parser
from time import sleep
from dateutil import parser
import sys
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

if anon_utils.Utils.is_prod_env():
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


def random_cimmot_node_generator():
    pass


def random_mod_file_node_generator():
    pass


def verify_k_anon(k_anon, main_node, link_type):
    start = 0
    jump = 300
    commit_nodes = node_maker.find_nodes(main_node, start, jump)

    logging.info(f"Verifying K anon - {k_anon}")

    while len(commit_nodes) != 0:

        commit_nodes = node_maker.find_nodes(main_node, start, jump)
        start += jump

        # get commits degree
        for commit in commit_nodes:

            if commit['id'] in blacklist_nodes:
                continue

            mod_files = node_maker.find_node_with_relation(main_node, commit['id'], link_type)

            val = degree_log.get(len(mod_files), [])
            val.append({"x": commit['id'], 'y': mod_files})
            degree_log[len(mod_files)] = val

    for k, v in degree_log.items():
        logging.info(f"K - {k} and V - {len(v)}")
        if len(v) < k_anon:
            logging.info(f"K anon not satisfied for k - {k} and v - {v}")
            # raise Exception(f"K anon not satisfied for k - {k} and v - {v}")

    logging.info("K anon satisfied")


if __name__ == '__main__':

    __start_time = time.time()

    nodes_altered = 0
    links_altered = 0

    start = 0
    jump = 300

    k_degree = 3
    if not anon_utils.Utils.is_local_env():
        k_degree = int(sys.argv[1])

    logging.info(f"K degree - {k_degree}")
    entity_type = [
        # this could leave some commits without any author as for each commit there is one author
        # we could give precendence to not removing author, but adding
        # TODO: maybe we can change reviewer



        (node_maker.COMMIT, node_maker.MOD_FILES, node_maker.LINK_MODIFYIED),
        (node_maker.PERSON, node_maker.PR, node_maker.LINK_REVIEWER),
        (node_maker.PERSON, node_maker.COMMIT, node_maker.LINK_WAS_AUTHORED_BY)
    ]

    try:
        for main_node, anony_node, link_type in entity_type:
            __main_loop_start_time = time.time()

            start = 0
            jump = 300

            # commit_nodes = node_maker.find_nodes(main_node, start, jump)

            if main_node != node_maker.COMMIT:
                commit_nodes = node_maker.find_nodes(main_node, start, jump)
            else:
                commit_nodes = node_maker.find_nodes_with_link_unique(main_node, node_maker.LINK_MODIFYIED, start,
                                                                         jump)

            # this stores the degree of the commit
            # this means which commit has how many mod files
            # commit x, y has 2 mod files
            # commit z has 3 mod files
            degree_log = {}

            extra_nodes_degree = []

            while len(commit_nodes) != 0:
                __commit_batch_start_time = time.time()

                if main_node != node_maker.COMMIT:
                    commit_nodes = node_maker.find_nodes(main_node, start, jump)
                else:
                    commit_nodes = node_maker.find_nodes_with_link_unique(main_node, node_maker.LINK_MODIFYIED, start,
                                                                          jump)
                start += jump

                # get commits degree
                for commit in commit_nodes:

                    if commit['id'] in blacklist_nodes:
                        logging.info(f"skipping {commit['id']}")
                        continue

                    __commit_start_time = time.time()

                    mod_files = node_maker.find_node_with_relation(main_node, commit['id'], link_type)

                    val = degree_log.get(len(mod_files), [])
                    val.append({"x": commit['id'], 'y': mod_files})
                    degree_log[len(mod_files)] = val

                    __commit_end_time = time.time()
                    # logging.info(f"commit - {commit['id']} time - {__commit_end_time - __commit_start_time}")

                # logging.info(degree_log)
                __commit_batch_end_time = time.time()
                logging.info(f"time batch - {__commit_batch_end_time - __commit_batch_start_time}")

            # for k anonymization
            # we need each degree to have more than k nodes
            # so now check the keys that have less than k nodes
            # for each degree which has more than k nodes we store it in extra_nodes_degree
            # we will use these additional nodes to add to the nodes which have less than k nodes
            for degree in degree_log.keys():
                logging.info(f"degree {degree} num {len(degree_log[degree])}")

                if len(degree_log[degree]) > k_degree:
                    extra_nodes_degree.append(degree)

            # now processing each degree
            for degree, nodes_in_degree in degree_log.items():

                logging.info(f"degree {degree} number of nodes {len(nodes_in_degree)}")

                if len(nodes_in_degree) > k_degree:
                    logging.info("skipping")
                    continue

                logging.info(f"Processing degree")
                # number of nodes to be added to this degree
                # to key (degree 4) we need to add diff number of nodes which have to be of degree 4
                diff = k_degree - len(nodes_in_degree)
                logging.info(f"diff {diff}")
                nodes_altered += diff

                # find the node that key which can be used to add diff number of nodes
                count = 0
                degree_which_has_surplus_nodes = None
                degree_found = False
                while count < len(extra_nodes_degree):
                    count += 1
                    degree_which_has_surplus_nodes = random.choice(extra_nodes_degree)


                    if len(degree_log[degree_which_has_surplus_nodes]) - k_degree - diff - 2 > 0:
                        logging.info(
                            f"degree_which_has_surplus_nodes {degree_which_has_surplus_nodes} which has {len(degree_log[degree_which_has_surplus_nodes])} nodes")
                        logging.info(f"k_degree {k_degree}")
                        logging.info(f"diff {diff}")
                        logging.info(
                            f"the match {len(degree_log[degree_which_has_surplus_nodes]) - k_degree - diff - 2}")
                        degree_found = True
                        break

                if degree_found is False:
                    logging.info(
                        f"key_which_has_surplus_nodes is None. Maybe have to increase jump or random node generation")
                    continue
                logging.info(f"degree_which_has_surplus_nodes {degree_which_has_surplus_nodes} which has {len(degree_log[degree_which_has_surplus_nodes])} nodes")

                # take this key, take diff number of nodes,
                for _ in range(diff):

                    # selecting a random element from the surplus nodes which will be performed
                    random.shuffle(degree_log[degree_which_has_surplus_nodes])
                    random_element = degree_log[degree_which_has_surplus_nodes].pop()

                    logging.info(f"degree {degree} random degree which is being added {degree_which_has_surplus_nodes}")

                    # suppose k = 3, degree 4 has 5 nodes, degree 3 has 2 nodes
                    # we need to add 1 node to degree 3 from degree 4
                    # so we will remove 1 node from degree 4, and add it to degree 3
                    if degree_which_has_surplus_nodes > degree:

                        # for each node, we need to remove this many nodes
                        number_of_nodes_to_remove = degree_which_has_surplus_nodes - degree
                        logging.info(f"Removing nodes {number_of_nodes_to_remove}")

                        for _ in range(number_of_nodes_to_remove):
                            # TODO: this will change, as we are removing nodes random ele structure changed a bit
                            # TODO: change the dict store we have
                            removal_link_entity = random_element["y"][0]['n']
                            # logging.info(f"remove id - {removal_link_entity['id']}")
                            node_maker.delete_link_of_id(main_node, anony_node, link_type, removal_link_entity['id'])
                            links_altered += 1

                    # so, degree 3 has 4 nodes, degree 4 has 2 nodes
                    # to make it 3, we need to add 1 node to degree 4
                    # we will take a node from degree 3, and add it to degree 4 by adds links for a node in degree 3
                    elif degree_which_has_surplus_nodes < degree:

                        number_of_nodes_to_add = degree - degree_which_has_surplus_nodes
                        logging.info(f"adding nodes {number_of_nodes_to_add}")

                        # find random nodes to add to the degree, finding random number of nodes, finding a random start
                        # point to find nodes from
                        __total_node = node_maker.count_node(anony_node)

                        try:
                            __random_start = random.randrange(0, __total_node - number_of_nodes_to_add)
                        except Exception as e:
                            logging.info(f"error {e}")
                            __random_start = 0

                        __anon_set_nodes = node_maker.find_nodes(anony_node, __random_start, number_of_nodes_to_add)

                        for __node in __anon_set_nodes:
                            # TODO: change this as we need, we need to randomly set the link size
                            property = {}
                            if link_type == node_maker.LINK_MODIFYIED:
                                # TODO: can get the file id, file type and then for all the nodes,
                                # find how manuch is it link changed and then fix it
                                property = {
                                    "la_link": random.randint(0, 200),
                                    "ld_link": random.randint(0, 200),
                                }
                            node_maker.link_nodes(main_node, random_element['x'], link_type, anony_node, __node['id'],
                                                  property)
                            # logging.info(f"addding n {__node}")
                            links_altered += 1

                        val = degree_log.get(degree, [])
                        val.append(random_element)
                        degree_log[degree] = val

            __main_loop_end_time = time.time()
            logging.info(
                f"entity {main_node} type - {anony_node} time - {__main_loop_end_time - __main_loop_start_time}")

            if os.environ.get("run_env", "prod") == "local":
                verify_k_anon(k_degree, main_node, link_type)

        __end_time = time.time()
        __data_dict = {
            "k": k_degree,
            "nodes_altered": nodes_altered,
            "links_altered": links_altered,
            "time": __end_time - __start_time,
            "current_time": datetime.datetime.now()
        }
        __file_name = f"k_da_node_infomration.csv"
        anon_utils.Utils.save_data_dict(__data_dict, __file_name)
    except Exception as e:
        logging.info(f" ERROR IN K ANON error {e}")
        raise e

    # , commit_id, tcmt, bugcount, fixcount, author_date, la, ld, ent, churn, nf, nd, ns, nuc, ndev, age, aexp, arexp, asexp



