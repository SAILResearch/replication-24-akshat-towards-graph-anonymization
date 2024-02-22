import logging
import os
import sys

import github.GithubException
from git import Repo
from pydriller import Repository, Commit, Git
from neo4j import GraphDatabase
from neo4j.exceptions import ConstraintError
from pandas import DataFrame
import datetime
from time import sleep
from scripts.anon_utils.utils import Utils as anon_utils
from NodeMaker import NodeMaker
from Utils import Utils
from neo.Neo4jConnection import Neo4jConnection

from github import Github
import pandas as pd
import datetime
from dateutil import parser
from time import sleep
import time
import warnings

warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("github_data.log"),
        logging.StreamHandler()
    ]
)



def get_project_path(project_name):
    return "repos/" + project_name


def clone_repositories(project_names):
    os.makedirs("repos", exist_ok=True)

    logging.info(f"Cloning {len(project_names)} repositories")
    for project_name in project_names:
        try:
            # clone using github remote url
            prefix = "https://github.com/"
            url = prefix + project_name
            # logging.info("Cloning " + url)
            try:
                Repo.clone_from(url, to_path="repos/" + project_name)
            except Exception as e:
                logging.info("Error cloning " + url)
                pass
            # git_repo = Repository(url, clone_repo_to="repos/" + project_name)
            git_repo = Git("repos/" + project_name)
            # print number of commits in repo
            logging.info(f"{url} - {git_repo.total_commits()}")


        except Exception as e:
            logging.info("Error cloning " + url)
            logging.info(e)
            continue

        # logging.info("Cloned " + project_name)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    df = pd.read_csv("apachejit_total.csv")

    # clone_repositories(df["project"].unique())

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

    node_maker.delete_all()
    node_maker.make_contraint()

    start_year = 2001
    end_year = 2020
    project = "apache/groovy"
    no_filter = False
    if anon_utils.is_prod_env():
        start_year = sys.argv[1]
        end_year = sys.argv[2]
        project = sys.argv[3]
        no_filter = bool(sys.argv[4])

    if no_filter:
        p_name = f"{project}.csv"
        print(f"No filter, so using the name given {p_name}")
        df = pd.read_csv(p_name)
        # project = "data_split_apache_ignite_train.csv"
        project = project.replace("data_split_", "").replace("_train", "")
        project = project.replace("_", "/")
        print(f"Project name is {project}")

    df_trimmed = pd.DataFrame()
    for year in range(int(start_year), int(end_year) + 1):
        # print("Filtering year " + str(year))
        df_trimmed = pd.concat([df_trimmed, df[df["year"] == year]])
        # df_trimmed = df_trimmed.append(df[df["year"] == year])
    df_trimmed = df_trimmed[df_trimmed["project"] == project]
    logging.info(f"Trimmed to {len(df_trimmed)} commits for project {project} and {df_trimmed.buggy.value_counts()}")

    # df_data = pd.read_csv('../../apachejit_total.csv')
    for __p in df["project"].unique():
        __temp_df = df[df["project"] == __p]
        # __df_data_temp = df_data[df_data["project"] == __p]

        project_path = get_project_path(__p)
        git_repo = Git(project_path)

        actual_commits_found = git_repo.get_list_commits()
        actual_commits_found = [c.hash for c in actual_commits_found]
        __temp_df = __temp_df[__temp_df["commit_id"].isin(actual_commits_found)]



        print(f"Project {__p} has {len(__temp_df)} commits and {len(__temp_df[__temp_df['buggy']])} buggy commits")

    for project in df_trimmed["project"].unique():

        project_path = get_project_path(project)
        git_repo = Git(project_path)
        df_project = df_trimmed[df_trimmed["project"] == project]
        logging.info(f"#"*40)

        logging.info(f"Doing project {project} with {len(df_project)} commits")
        count = 0
        for index, row in df_project.iterrows():
            count += 1

            logging.info(f"*"*40)
            logging.info(f"Progress {count} of {len(df_project)} - {100 * count/len(df_project)}%")

            logging.info(f"Doing commit {row['commit_id']}")
            commit = git_repo.get_commit(row["commit_id"])

            node_maker.make_commit_node(commit)

            author_name = commit.author.name
            node_maker.make_person_node(author_name)
            node_maker.link_nodes(node_maker.COMMIT, row["commit_id"], node_maker.LINK_WAS_AUTHORED_BY,
                                  node_maker.PERSON, author_name)

            committer_name = commit.committer.name
            node_maker.make_person_node(committer_name)
            node_maker.link_nodes(node_maker.COMMIT, row["commit_id"], node_maker.LINK_COMMITTED,
                                  node_maker.PERSON, committer_name)

            logging.info(f"Committers {commit.committer.name} author {commit.author.name}")

            for parent in commit.parents:
                parent_commit = git_repo.get_commit(parent)
                node_maker.make_commit_node(parent_commit)
                node_maker.link_nodes_bidirectional(node_maker.COMMIT, row["commit_id"], node_maker.LINK_CHILD,
                                      node_maker.COMMIT, parent, node_maker.LINK_PARENT)

            for file in commit.modified_files:
                logging.info(f"File {file.filename} lines added {file.added_lines} lines removed {file.deleted_lines}")
                node_maker.make_mod_files(file)
                node_maker.link_nodes(node_maker.COMMIT, commit.hash, node_maker.LINK_MODIFYIED,
                                      node_maker.MOD_FILES, file.new_path,
                                      Utils.make_file_change_dict(file))



        # for commit in Repository(project_path, order='reverse').traverse_commits():
        #
        #     logging.info(commit.hash)
        #
        #     break
        #
        # break
        #
