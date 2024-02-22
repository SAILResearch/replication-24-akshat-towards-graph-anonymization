#!/usr/bin/env bash


dataset=$1
echo "Running partition_data_process.sh for $dataset"

echo "Running split"
python3 scripts/misc/train_test_id_split.py $dataset

new_dataset_name="data_split_"$dataset"_train"
echo "new_dataset_name = $new_dataset_name"

echo "Create graph"

# if name is openstack or qt, then use gerrit_data.py
# else use github_graph_data.py
if [ "$dataset" = "openstack" ] || [ "$dataset" = "qt" ]; then
    echo "openstack or qt"
    python3 gerrit_data.py $new_dataset_name
else
    echo "not openstack"
    python3 github_graph_data.py 2000 2023 $new_dataset_name True
fi

bash scripts/automation/save_graph.sh $new_dataset_name

