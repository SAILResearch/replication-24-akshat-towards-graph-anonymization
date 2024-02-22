#!/usr/bin/env bash


# takes the name of the experiment as an argument
# e.g. ./random_automate_experiment.sh fabric_k_anon
# take param from command line
dataset=$1
#dataset="openstack"
experiment_name_prefix="gen"
graph_data_prefix="graph_csv_dump"

# create a folder for the experiment
mkdir "anon_results"/$dataset
mkdir "anon_results"/$dataset/$experiment_name_prefix
experiment_name=$dataset"_"$experiment_name_prefix

echo "restore database"
echo "restore database" >> output.txt
bash scripts/automation/restore_db.sh $dataset

echo "moving results"
echo "moving results" >> output.txt
mv "anon_results"/$dataset/$experiment_name_prefix/$dataset* "anon_results"/$dataset/$experiment_name_prefix/"save"
mv $dataset"_"$experiment_name_prefix* dataDump/


# run the randomisation script for 5 times
cluser_size=100
k_value=10

for i in 10 15 20 25 30 40 50 65 80 100
do

    # start timer
    start=`date +%s`

    # create a folder for the experiment
    experiment_name_run=$experiment_name"_"$i
    echo "experiment_name_run = $experiment_name_run"

    # run the randomisation script
    echo "randomise experiment_name_run = $experiment_name_run"
    echo "randomise experiment_name_run = $experiment_name_run" >> output.txt
    python scripts/random/generalization.py $k_value $i >> output.txt

    # copy the graph
    echo "copy graph csv" >> output.txt
    bash scripts/automation/dump_graph_csv.sh "anon_results"/$dataset/$experiment_name_prefix/$graph_data_prefix"_"$experiment_name_run".csv"


    # create stats with experiment name and iteration number
    echo "compute stats"
    echo "compute stats" >> output.txt
    python compute_stats.py $experiment_name_run $dataset >> output.txt

    end=`date +%s`

    # compute time taken
    runtime=$((end-start))
    echo "runtime = $runtime"

    # save it to a file
    echo $experiment_name_run >> time.txt
    echo $runtime >> time.txt

    echo "restore database"
    echo "restore database" >> output.txt
    bash scripts/automation/restore_db.sh $dataset


done



echo "restore database"
echo "restore database" >> output.txt
bash scripts/automation/restore_db.sh $dataset
echo $experiment_name >> output.txt
python compute_stats.py $experiment_name"_non_anon" $dataset
bash scripts/automation/dump_graph_csv.sh "anon_results"/$dataset/$experiment_name_prefix/$graph_data_prefix"_"$experiment_name"_non_anon.csv"



cp "$experiment_name"* "anon_results"/$dataset/$experiment_name_prefix

#find . -type f -name "$experiment_name*" -print0 | while IFS= read -r -d '' file; do
#    echo "file = $file"
#    cp "$file" "anon_results"/$dataset/$experiment_name_prefix/
#done

