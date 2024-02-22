import os
import sys
from time import sleep

import pandas as pd
import requests
import json

from pprint import pprint
from NodeMaker import NodeMaker
from neo.Neo4jConnection import Neo4jConnection

url = "https://review.opendev.org/changes/{commit}/detail/?o=CURRENT_REVISION&o=DETAILED_LABELS&o=ALL_COMMITS&o=ALL_FILES"

headers = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Cookie": "ai_user=Q2FcXSdbfP6ugxp5HPIun2|2023-02-05T21:00:10.631Z; mod_auth_openidc_session=f5f95112-670d-40d8-90bc-635be4f66676; GerritAccount=aQFAprqNlHxn8iqKJofJJ.z-NkcAFjvNDW; XSRF_TOKEN=aQFAprsEEX55dws7RYOmxQcypWB203xzIW",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "macOS"
}

def get_name_from_dict(name_data):
    if "email" in name_data:
        return name_data["email"]
    elif "username" in name_data:
        return name_data["username"]
    elif "name" in name_data:
        return name_data["name"]
    elif "_account_id" in name_data:
        return name_data["_account_id"]
    else:
        return None

def get_mod_dict(_key, _value):
    return {

        "old_path": _key,
        "new_path": _key,
        "filename": os.path.basename(_key),

        "la": _value.get("lines_inserted", 0),
        "ld": _value.get("lines_deleted", 0),

        "directory": os.path.dirname(_key) if _key is not None else None,
        "subsystem": os.path.normpath(_key).split(os.path.sep)[0] if _key is not None else None

    }


def get_parent_dict(url, headers, _item):
    __request_url = url.replace("{commit}", _item["commit"])
    __parent_response = requests.get(__request_url, headers=headers)

    parent_commit_dict = {
        "sha": _item["commit"],
    }

    if __parent_response.status_code != 200:
        print("parent not found")
        return parent_commit_dict

    __parent_data = json.loads(__parent_response.content.decode("utf-8").replace(")]}'\n", ""))

    if len(__parent_data) == 0:
        print("No parent data found")
        return parent_commit_dict
    # __parent_data = __parent_data[0]


    if "qt" in dataset:
        __parent_data = __parent_data[-1]
                

    # __parent_data = __parent_response.content.decode()[5:]
    # __parent_data = json.loads(__parent_data)

    parent_commit_dict = {
                    "author_date": __parent_data.get("created", None),
                    "sha": _item["commit"],
                    "la": __parent_data.get("insertions", 0),
                    "ld": __parent_data.get("deletions", 0)
                }
        
    return parent_commit_dict

if __name__ == "__main__":

    if os.environ.get('run_env', 'prod') == 'prod':
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

    project_name = sys.argv[1]
    if "openstack" in project_name:
        dataset = f"{project_name}.csv"
        url = "https://review.opendev.org/changes/{commit}/detail/?o=CURRENT_REVISION&o=DETAILED_LABELS&o=ALL_COMMITS&o=ALL_FILES"
    elif "qt" in project_name:
        dataset = f"{project_name}.csv"
        # url = "https://codereview.qt-project.org/changes/{commit}/detail/?o=CURRENT_REVISION&o=DETAILED_LABELS&o=ALL_COMMITS&o=ALL_FILES"
        url = "https://codereview.qt-project.org/changes/?q={commit}&o=CURRENT_REVISION&o=DETAILED_LABELS&o=ALL_COMMITS&o=ALL_FILES"
    else:
        print("Invalid project name")
        raise Exception("Invalid project name")




    node_maker = NodeMaker(conn)

    node_maker.delete_all()
    node_maker.make_contraint()

    limit = 2000
    sleep_delay = 0
    # dataset = "openstack.csv"
    
    df = pd.read_csv(dataset)
    print(f"Project name: {project_name}")
    print(f"Dataset: {dataset}")
    print(f"Total commits: {len(df)}")
    print(f"URL: {url}")

    start_offset = 0
    for index, row in df.iloc[start_offset:].iterrows():
        
        # limit -= 1
        # if limit <= 0:
            #break
        
        commit = row["commit_id"]
        
        # get data from gerrit
        # commit = "f513e88403b66c4a5efe4c62c160dfce151efb33"
        
        print("*" * 100)
        print(f"index: {index} / {len(df)} percent done {100*index/len(df)} commit: {commit}")


        # filter data based on time
        if "openstack" in dataset:
            if not(1322599384 <= row["author_date"] <= 1393590700):
                print("Commit incorrect time continue")
                continue
            else:
                print("going ahead")
        elif "qt" in dataset:
            # if not(1308350292 <= row["author_date"] <= 1395090476):
            #     print("Commit incorrect time continue")
            #     continue
            # else:
            print("going ahead")
        else:
            print("Invalid dataset")
            raise Exception("Invalid dataset")
            

        request_url = url.replace("{commit}", commit)
        response = requests.get(request_url, headers=headers)

        if response.status_code != 200:
            sleep(sleep_delay)
            print("Request failed, continue to next commit")
            continue

        # data = response.content.decode()[5:]
        # data = json.loads(data)
        data = json.loads(response.content.decode("utf-8").replace(")]}'\n", ""))
        if len(data) == 0:
            print("No data found")
            continue
        if "qt" in dataset:
            data = data[-1]

        # construct the commit dict
        commit_dict = {
            "author_date": data["created"],
            "sha": commit,
            "la": data["insertions"],
            "ld": data["deletions"]
        }
        node_maker.make_commit_node(None, commit_dict=commit_dict)
        
        
        # find the owner and its name
        if "owner" not in data:
            print("owner not in data")
            continue
        
        author = get_name_from_dict(data["owner"])
        if author is None:
            print("Cannot find author name")
            continue
            
        # make the author of the commit
        node_maker.make_person_node(author)
        node_maker.link_nodes(node_maker.COMMIT, commit_dict["sha"], node_maker.LINK_WAS_AUTHORED_BY, node_maker.PERSON, author)

        # make the submitter/merger of the commit
        submitter = None
        if "submitter" in data:
            submitter = get_name_from_dict(data["submitter"])
            node_maker.make_person_node(submitter)
            node_maker.link_nodes(node_maker.PERSON, submitter, node_maker.LINK_COMMITTED, node_maker.COMMIT, commit_dict["sha"])

        print(f"author: {author} submitter: {submitter}")
        
        # find the files modified in the commit
        # also for each parent commit, get their details
        for key, value in data["revisions"].items():
            for _key, _value in value["files"].items():
                print(f"file: {_key}")
                mod_file = get_mod_dict(_key, _value)
                node_maker.make_node(node_maker.MOD_FILES, mod_file["new_path"], mod_file)
                node_maker.link_nodes(node_maker.COMMIT, commit_dict["sha"], node_maker.LINK_MODIFYIED, node_maker.MOD_FILES, mod_file["new_path"],
                                      {"la_link": _value.get("lines_inserted", 0), "ld_link": _value.get("lines_deleted", 0)})

            # for each parent commit, get their details
            for _item in value["commit"]["parents"]:
                print(f"parent: {_item['commit']}")
                
                parent_commit_dict = get_parent_dict(url, headers, _item)
                node_maker.make_commit_node(None, parent_commit_dict)
                node_maker.link_nodes_bidirectional(node_maker.COMMIT, commit_dict["sha"], node_maker.LINK_CHILD,
                                                    node_maker.COMMIT, parent_commit_dict["sha"], node_maker.LINK_PARENT)

        # now get change related details
        
        change_id = data["change_id"]

        # get approvers
        approver_emails = set()
        reviewer_emails = set()
        if "labels" in data and "Code-Review" in data["labels"] and "all" in data["labels"]["Code-Review"]:
            for approved in data["labels"].get("Code-Review").get("all", []):
                if approved.get("value", -1) > 0:
                    _name = get_name_from_dict(approved)
                    if _name is not None:
                        approver_emails.add(_name)

        # get reviewers
        reviewers_dict = []
        if "messages" in data:
            reviewers_dict = data["messages"]
        elif "labels" in data and "Code-Review" in data["labels"] and "all" in data["labels"]["Code-Review"]:
            reviewers_dict = data["labels"].get("Code-Review").get("all")
            if 'Sanity-Review' in data["labels"]:
                reviewers_dict.extend(data["labels"].get("Sanity-Review").get("all", []))

        if len(reviewers_dict) == 0:
            print("No reviewers found")

        # get the approval date
        approval_date = None
        for approved in reviewers_dict:
            if "value" in approved and approved["value"] > 0:
                if "date" in approved:
                    date = approved["date"]
                    if approval_date is None or date > approval_date:
                        approval_date = date
                else:
                    print("Warning: Approval date is not available")
        approval_date  = data["updated"] if "updated" in data else approval_date

        # get the nrev
        try:
            nrev = list(data.get("revisions", {}).values())[0]["_number"]
        except Exception as e:
            print(e)
            nrev = 0
            
        
        # make the pr dict to make the pr node
        pr_dict = {
            "id": change_id,
            "created_at": data["created"],
            "merged_at": data.get("submitted", None),
            "approval_date": approval_date,
            "comments": len(data.get("messages", [])),
            "nrev": nrev
        }
        node_maker.make_node(node_maker.PR, change_id, pr_dict)
        



        for reviewed in reviewers_dict:
            
            if "author" in reviewed.keys() and project_name == "openstack":
                _author = reviewed["author"]
                _name = get_name_from_dict(_author)
                if _name is not None:
                    reviewer_emails.add(_name)

            if project_name == "qt":
                _name = get_name_from_dict(reviewed)
                if _name is not None:
                    reviewer_emails.add(_name)

        print(f"reviewers: {reviewer_emails}")
        print(f"approvers: {approver_emails}")

        # add reviewers
        for reviewer in reviewer_emails:
            node_maker.make_person_node(reviewer)
            node_maker.link_nodes(node_maker.PR, change_id, node_maker.LINK_REVIEWER, node_maker.PERSON, reviewer)

        # add approvers
        for approver in approver_emails:
            node_maker.make_person_node(approver)
            node_maker.link_nodes(node_maker.PR, change_id, node_maker.LINK_APPROVER, node_maker.PERSON, approver)

        node_maker.link_nodes(node_maker.COMMIT, commit, node_maker.LINK_PART_OF, node_maker.PR, change_id)
        
        for _revision, _data in data["revisions"].items():
            _commit_dict = {
                "author_date": _data["created"],
                "sha": _revision,
                "la": sum(item.get('lines_inserted', 0) for item in _data["files"].values()),
                "ld": sum(item.get('lines_deleted', 0) for item in _data["files"].values())
            }

            node_maker.make_commit_node(None, _commit_dict)
            node_maker.link_nodes(node_maker.COMMIT, _commit_dict["sha"], node_maker.LINK_PART_OF,  node_maker.PR, change_id)


        # break
        print("Completed commit: ", commit)
        sleep(sleep_delay)

