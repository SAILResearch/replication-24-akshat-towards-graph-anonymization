import os
import random
import sys
import time

from pydriller import Repository, Commit
from neo4j import GraphDatabase
from neo4j.exceptions import ConstraintError
from pandas import DataFrame
import datetime
from time import sleep
from NodeMaker import NodeMaker
from Utils import Utils
from scripts.anon_utils import utils as anon_utils
from neo.Neo4jConnection import Neo4jConnection

from github import Github
import pandas as pd
import datetime
from dateutil import parser
from time import sleep
from dateutil import parser

if __name__ == '__main__':
    if not anon_utils.Utils.is_local_env():
        conn = Neo4jConnection(uri="bolt://localhost:7687",
                               user="neo4j",
                               pwd="password",
                               db="graph.db")
        parallel_workers = 100
        ANONYMITY_PERCENT = int(sys.argv[1])
    else:
        conn = Neo4jConnection(uri="bolt://localhost:11014",
                               user="neo4j",
                               pwd="password",
                               db="major")
        ANONYMITY_PERCENT = 20

    node_maker = NodeMaker(conn)


    ANONYMOUS_NODE = [node_maker.COMMIT, node_maker.PERSON]
    LEFT_TO_RIGHT = "left_to_right"
    RIGHT_TO_LEFT = "right_to_left"

    nodes_changed = 0
    links_changed = 0
    __start_time = time.time()
    
    LINK_DEFINITION = {

        node_maker.COMMIT: [
            (node_maker.LINK_MODIFYIED, node_maker.MOD_FILES, LEFT_TO_RIGHT),

            # (node_maker.LINK_WAS_AUTHORED_BY, node_maker.PERSON, LEFT_TO_RIGHT),
            # (node_maker.LINK_WRITTEN_BY, node_maker.PERSON, RIGHT_TO_LEFT),
            # (node_maker.LINK_COMMITTED, node_maker.PERSON, LEFT_TO_RIGHT),

            (node_maker.LINK_PART_OF, node_maker.PR, LEFT_TO_RIGHT),
        ],

        # write all the links that are present in the graph
        node_maker.PERSON: [
            (node_maker.LINK_WAS_AUTHORED_BY, node_maker.COMMIT, RIGHT_TO_LEFT),
            # (node_maker.LINK_COMMITTED, node_maker.COMMIT, LEFT_TO_RIGHT),
            # (node_maker.LINK_WRITTEN_BY, node_maker.COMMIT, LEFT_TO_RIGHT),

            (node_maker.LINK_REVIEWER, node_maker.PR, RIGHT_TO_LEFT),
            (node_maker.LINK_APPROVER, node_maker.PR, RIGHT_TO_LEFT)]
    }

    for key, value in LINK_DEFINITION.items():
        total_nodes = node_maker.count_node(key)
        number_to_change = int(ANONYMITY_PERCENT * total_nodes / 100)
        print(f"Total people {total_nodes} and random {number_to_change}")

        if key != node_maker.COMMIT:
            nodes_to_change = node_maker.find_nodes(key, 0, total_nodes)
        else:
            nodes_to_change = node_maker.find_nodes_with_link_unique(key, node_maker.LINK_MODIFYIED, 0, total_nodes)
        nodes_to_change = [x['id'] for x in nodes_to_change]

        # make sure this is even
        random_select = random.sample(nodes_to_change, number_to_change)
        if len(random_select) % 2 == 1:
            random_select.append(random.sample(nodes_to_change, 1)[0])


        # random_select = ["a30c3cc287de122be0d31cb7e974c063c74ac04d", "3a0e164308dbf76322cc7473f6181694ca7e4867"]


        for i in range(0, len(random_select), 2):
            
            nodes_changed += 2
            
            first_node_id = random_select[i]
            second_node_id = random_select[i + 1]

            print(f"i {i} {first_node_id} to {second_node_id}")

            for el in LINK_DEFINITION[key]:

                link_type = el[0]
                link_entity = el[1]
                direction = el[2]

                # save links that first node has
                d_first_info = node_maker.find_node_with_relation(key, first_node_id, link_type)

                # save links that second node has
                d_second_info = node_maker.find_node_with_relation(key, second_node_id, link_type)

                # delte links both nodes have
                node_maker.delete_links_of_type(key, first_node_id, link_type)
                node_maker.delete_links_of_type(key, second_node_id, link_type)
                links_changed += len(d_first_info) + len(d_second_info)

                # assign first, second links
                for d_links in d_first_info:

                    if direction == LEFT_TO_RIGHT:
                        type_1 = key
                        id_1 = second_node_id
                        type_2 = link_entity
                        id_2 = d_links['b']['id']
                        relation_dict = d_links['r']['properties']
                    else:
                        type_1 = link_entity
                        id_1 = d_links['b']['id']
                        type_2 = key
                        id_2 = second_node_id
                        relation_dict = d_links['r']['properties']

                    node_maker.link_nodes(type_1, id_1, link_type, type_2, id_2, relation_dict)
                    links_changed += 1

                # assign second, first links
                for d_links in d_second_info:

                    if direction == LEFT_TO_RIGHT:
                        type_1 = key
                        id_1 = first_node_id
                        type_2 = link_entity
                        id_2 = d_links['b']['id']
                        relation_dict = d_links['r']['properties']
                    else:
                        type_1 = link_entity
                        id_1 = d_links['b']['id']
                        type_2 = key
                        id_2 = first_node_id
                        relation_dict = d_links['r']['properties']

                    node_maker.link_nodes(type_1, id_1, link_type, type_2, id_2, relation_dict)
                    links_changed += 1
    
    __end_time = time.time()
    change_data_dict = {
        "nodes_changed" : nodes_changed,
        "links_changed" : links_changed,
        "time_taken" : __end_time - __start_time,
        "date" : datetime.datetime.now(),
        "anonymity_percent" : ANONYMITY_PERCENT
    }
    __storage_file_name = "random_switch_anonymity.csv"
    anon_utils.Utils.save_data_dict(change_data_dict, __storage_file_name)
