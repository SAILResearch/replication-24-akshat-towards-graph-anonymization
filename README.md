PDF can be found here - https://mcis.cs.queensu.ca/publications/2024/emse_akshat_within.pdf

# Replication Package for Graph Anonymization

Before running the code, please install the items need to be setup:
- Python 3.6
- Python 2.7
- Java 8
- Neo4j 3.5.14

## 1. Graph Creation

To create the graph using the following command:

```bash
bash scripts/automation/partition_data_process.sh <repository-name>
bash scripts/automation/save_graph.sh data_split_<repository-name>_train
```


## 2. Anonymize the graph using the graph anonymization techniques

```bash
bash scripts/automation/random_add_delete_automate_experiment.sh data_split_<repository-name>_train
python scripts/automation/split_measure_privacy_and_predictive_power.py data_split_<repository-name>_train_random_add_delete anon_results/data_split_<repository-name>_train/random_add_delete/

bash scripts/automation/random_switch_automate_experiment.sh data_split_<repository-name>_train
python scripts/automation/split_measure_privacy_and_predictive_power.py data_split_<repository-name>_train_random_switch anon_results/data_split_<repository-name>_train/random_switch/

bash scripts/automation/k_anonymity.sh data_split_<repository-name>_train
python scripts/automation/split_measure_privacy_and_predictive_power.py data_split_<repository-name>_train_k_da_anon anon_results/data_split_<repository-name>_train/k_da_anon/

bash scripts/automation/generalisation.sh data_split_<repository-name>_train
python scripts/automation/split_measure_privacy_and_predictive_power.py data_split_<repository-name>_train_gen anon_results/data_split_<repository-name>_train/gen/
```


This should generate all the data images in the `anon_results` folder. However, this is a very time consuming task. 
To skip the above steps, we have provided the data in the `all_graph_anonymized_file.gz`. 
The data should then be stored in the `anon_results` folder.
Download the files from the following link: https://github.com/SAILResearch/replication-24-akshat-towards-graph-anonymization/releases/tag/v1

After extracting the files, run the `split_measure_privacy_and_predictive_power.py` file to generate the cleaned up version of the data. 

## 3. Run the LACE file for comprision

```bash
python2 lace_test/LACE/lace_baseline.py <repository-name>
python scripts/automation/lace_comparision.py <repository-name> 
```


## 4. Generate analysis files

Using the following command to generate the analysis files:

```bash
python scripts/misc/data_split_rq1_analysis.py
python scripts/misc/data_split_rq2_analysis.py
python scripts/misc/data_split_rq3_analysis.py
python scripts/misc/data_split_rq4_lace_comp.py
```




