#!/usr/bin/env bash

datbase_name=$1
echo "datbase_name = $datbase_name"
echo "datbase_name = $datbase_name" >> output.txt
database_dump_name="/home/local/SAIL/akshat/neo4j-community-3.5.0/"$datbase_name".dump"

echo "database_dump_name = $database_dump_name"
echo "database_dump_name = $database_dump_name" >> output.txt

echo "restore database"
echo "restore database" >> output.txt

echo "stopping db"
echo "stopping db" >> output.txt
/home/local/SAIL/akshat/neo4j-community-3.5.0/bin/neo4j stop
sleep 30s

echo "restore db"
echo "restore db" >> output.txt
/home/local/SAIL/akshat/neo4j-community-3.5.0/bin/neo4j-admin load --from=$database_dump_name --database=graph.db --force
sleep 30s

echo "start db"
echo "start db" >> output.txt
/home/local/SAIL/akshat/neo4j-community-3.5.0/bin/neo4j start
sleep 30s
