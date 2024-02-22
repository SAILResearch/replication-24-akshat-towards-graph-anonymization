#!/usr/bin/env bash

/home/local/SAIL/akshat/neo4j-community-3.5.0/bin/neo4j stop

dataset_name=$1
dataset_file="/home/local/SAIL/akshat/neo4j-community-3.5.0/"$dataset_name".dump"

echo "dataset_file = $dataset_file"

# get a random seed



# save the previous graph
random_seed=$(python -c 'import random; print(random.randint(0, 1000000000))')
mv "/home/local/SAIL/akshat/neo4j-community-3.5.0/"$dataset_name".dump" "/home/local/SAIL/akshat/neo4j-community-3.5.0/backup_"$dataset_name"_"$random_seed".dump"



# create the new graph
/home/local/SAIL/akshat/neo4j-community-3.5.0/bin/neo4j-admin dump --database=graph.db --to="/home/local/SAIL/akshat/neo4j-community-3.5.0/"$dataset_name".dump"



# save it in another place
random_seed=$(python -c 'import random; print(random.randint(0, 1000000000))')
cp "/home/local/SAIL/akshat/neo4j-community-3.5.0/"$dataset_name".dump" "/home/local/SAIL/akshat/neo4j-community-3.5.0/backup_"$dataset_name"_"$random_seed".dump"
cp "/home/local/SAIL/akshat/neo4j-community-3.5.0/"$dataset_name".dump" "/home/local/SAIL/akshat/backup_"$dataset_name"_"$random_seed".dump"



/home/local/SAIL/akshat/neo4j-community-3.5.0/bin/neo4j start