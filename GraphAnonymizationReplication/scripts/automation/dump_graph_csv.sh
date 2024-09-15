#!/usr/bin/env bash

# get the name of the experiment from the command line
file_path=$1

rm /home/local/SAIL/akshat/GraphAnon/movies.csv
echo "moving file"
echo "moving file" >> output.txt
../neo4j-community-3.5.0/bin/cypher-shell 'CALL apoc.export.csv.all("/home/local/SAIL/akshat/GraphAnon/movies.csv", {})'
mv /home/local/SAIL/akshat/GraphAnon/movies.csv $file_path
