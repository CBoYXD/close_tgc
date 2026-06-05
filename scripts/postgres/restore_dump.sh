#!/bin/bash

source .env

if [ ! -d scripts/postgres/dumps ];
then
    echo "dumps folder does not exist"
else
    read -p "Enter unique name of db_dump: " name_of_db_dump

    docker cp scripts/postgres/dumps/${name_of_db_dump}.backup ${DB_HOST}:/tmp/${name_of_db_dump}.backup
    docker exec -t ${DB_HOST} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f tmp/${name_of_db_dump}.backup
fi
