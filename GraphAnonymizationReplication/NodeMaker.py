from github import PullRequest
from neo4j.exceptions import ConstraintError
from pydriller import Commit, ModifiedFile

from Utils import Utils


class NodeMaker:
    LINK_WAS_AUTHORED_BY = "WAS_AUTHORED_BY"
    LINK_WRITTEN_BY = "WRITTEN_BY"
    LINK_BRANCH = "IN_BRANCH"
    LINK_MODIFYIED = "MODIFYED"
    LINK_COMMITTED = "COMMITTED"
    LINK_CHILD = "CHILD"
    LINK_PARENT = "PARENT"
    LINK_REVIEWER = "REVIEWER"
    LINK_APPROVER = "APPROVER"
    LINK_PART_OF = "PART_OF"

    COMMIT = "Commit"
    PERSON = "Person"
    BRANCH = "Branch"
    MOD_FILES = "ModFiles"
    PR = "PR"

    def __init__(self, conn):
        self.__conn = conn

    def make_contraint(self):
        for node_name in ["Commit", "Person", "Branch", "ModFiles", "PR"]:
            #self.__conn.query(
             #   f'CREATE CONSTRAINT {node_name.lower()}Unique IF NOT EXISTS ON (a:{node_name}) ASSERT a.id IS UNIQUE;')
            self.__conn.query(
                f'CREATE CONSTRAINT  ON (a:{node_name}) ASSERT a.id IS UNIQUE;')

    def make_props_string(self, props: dict):
        if props is None:
            return ""

        if len(props.keys()) == 0:
            return "{}"
        
        props_string = " { "
        key = list(props.keys())[0]
        props_string += f"{key}: \"{props.get(key)}\""

        for i in range(1, len(props.keys())):
            key = list(props.keys())[i]
            props_string += f" , {key}: \"{props.get(key)}\""

        props_string += " } "
        return props_string

    def make_node(self, node_type: str, node_id: str, props: dict = None):
        props_string = self.make_props_string(props)
        try:
            if props is None:
                self.__conn.query(f"""create (a:{node_type}) set a.id = '{node_id}' """)
            else:
                self.__conn.query(f"""create (a:{node_type} {props_string}) set a.id = '{node_id}' """)
        except ConstraintError:
            # print("Node already exists " + node_id)
            pass

    def make_commit_node(self, commit: Commit, commit_dict=None):
        if commit_dict is None:
            commit_dict = Utils.make_commit_dict(commit)
        self.make_node(self.COMMIT, commit_dict["sha"], commit_dict)

    def make_person_node(self, name: str):
        self.make_node(self.PERSON, name)

    def make_pr_node(self, pr: PullRequest):
        pr_dict = Utils.make_pr_dict(pr)
        self.make_node(self.PR, pr.number, pr_dict)

    def make_branch(self, name: str):
        self.make_node(self.BRANCH, name)

    def make_mod_files(self, file: ModifiedFile):
        modfile_dict = Utils.make_mod_file_dict(file)
        self.make_node(self.MOD_FILES, file.new_path, modfile_dict)

    def link_nodes(self, node_type_1, node_type_1_id, link_name, node_type_2, node_type_2_id,
                   relation_params_dict: dict = None):
        if link_name == self.LINK_MODIFYIED and relation_params_dict in [None, {}]:
            raise Exception("Relation params is required for MODIFIED link")
            
        relation_params_string = self.make_props_string(relation_params_dict)
        self.__conn.query(
            f"""match (a:{node_type_1}), (b:{node_type_2}) 
        where a.id = '{node_type_1_id}' and b.id = '{node_type_2_id}' 
        create (a)-[r:{link_name} {relation_params_string if relation_params_dict is not None else ""} ]->(b)""")

    def link_nodes_bidirectional(self, node_type_1, node_type_1_id, link_name_1, node_type_2, node_type_2_id,
                                 link_name_2):
        self.link_nodes(node_type_1, node_type_1_id, link_name_1, node_type_2, node_type_2_id)
        self.link_nodes(node_type_2, node_type_2_id, link_name_2, node_type_1, node_type_1_id)

    def find_nodes(self, node_type, skip=0, limit=100):
        response = self.__conn.query(f""" match (n:{node_type}) return n skip {skip} limit {limit} """)
        return_data = []
        for res in response:
            return_data.append(res.data()['n'])
        return return_data

    def find_nodes_with_link_unique(self, node_type, node_link, skip=0, limit=100):
        response = self.__conn.query(f""" match (n:{node_type})-[:{node_link}]-() return distinct n skip {skip} limit {limit} """)
        return_data = []
        for res in response:
            return_data.append(res.data()['n'])
        return return_data

    def delete_all(self):
        res = self.__conn.query(f""" match (n) detach delete n """)
    
    def find_node_with_relation(self, node_type, node_type_id, relation_type):
        response = self.__conn.query(f""" match (n:{node_type} {{ id: '{node_type_id}' }} )-[r:{relation_type}]-(b) return n, r, b """)
        return_data = []
        for res in response:
            _data = res.data()
            relation_details = {
                "type" : res.data()['r'][1],
                "properties": dict(res['r'])
            }
            _data['r'] = relation_details
            return_data.append(_data)
        return return_data

    def count_node(self, node_type):
        res = self.__conn.query(f""" match (n:{node_type}) return count(n) as e """)
        return int(res[0].data()["e"])


    def delete_links_of_type(self, node_type, node_type_id, relation_type):
        self.__conn.query(f""" match (p:{node_type} {{ id : '{node_type_id}' }} ) -[r:{relation_type}]-(b) delete r """)

    def delete_link_of_id(self, node_type, node_type_id, relation_type, related_id):
        self.__conn.query(f""" match (p:{node_type} {{ id : '{node_type_id}' }} ) -[r:{relation_type}]-(b {{ id : '{related_id}' }} ) delete r """)

