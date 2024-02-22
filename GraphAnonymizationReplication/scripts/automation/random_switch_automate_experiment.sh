#!/usr/bin/env bash


# takes the name of the experiment as an argument
# e.g. ./random_automate_experiment.sh fabric_k_anon
dataset=$1
experiment_name_prefix="random_switch"
graph_data_prefix="graph_csv_dump"


# create a folder for the experiment
mkdir "anon_results"/$dataset
mkdir "anon_results"/$dataset/$experiment_name_prefix
experiment_name=$dataset"_"$experiment_name_prefix

echo "restore database"
echo "restore database" >> output.txt
bash scripts/automation/restore_db.sh $dataset

# moving results
echo "moving results"
echo "moving results" >> output.txt
mv "anon_results"/$dataset/$experiment_name_prefix/$dataset* "anon_results"/$dataset/$experiment_name_prefix/"save"
mv $dataset"_"$experiment_name_prefix* dataDump/

total=0
# run the randomisation script for 5 times
for i in 2 2 2 2 2 2 2 2 2 2 10 10 10 10 10 10 10 10
do

    echo "i = $i"
    echo "i = $i" >> output.txt
    total=$((total+i))
    echo "iteration = $i"
    echo "iteration = $i" >> output.txt
    echo "total = $total"
    echo "total = $total" >> output.txt

    # start timer
    start=`date +%s`
    
    # create a folder for the experiment
    experiment_name_run=$experiment_name"_"$total
    echo "experiment_name_run = $experiment_name_run"

    # run the randomisation script
    echo "randomise experiment_name_run = $experiment_name_run" 
    echo "randomise experiment_name_run = $experiment_name_run" >> output.txt
    python scripts/random/random_switch.py $i
    
    # copy the graph 
    echo "copy graph csv" >> output.txt
    bash scripts/automation/dump_graph_csv.sh "anon_results"/$dataset/$experiment_name_prefix/$graph_data_prefix"_"$experiment_name_run".csv"


    # create stats with experiment name and iteration number

    echo "compute stats"
    echo "compute stats" >> output.txt
    python compute_stats.py $experiment_name_run $dataset
    
    end=`date +%s`

    # compute time taken
    runtime=$((end-start))
    echo "runtime = $runtime"
    
    # save it to a file
    echo $experiment_name_run >> time.txt
    echo $runtime >> time.txt
    
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

