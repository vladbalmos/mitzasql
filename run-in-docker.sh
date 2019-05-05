#!/bin/bash

# Use this script to run tests or mitzasql using different versions of python and/or mysql server versions

if [ -z "$1" ]; then
    echo "Missing python version (Ex: $0 35 mysql55)"
    exit 1
fi

if [ -z "$2" ]; then
    echo "Missing mysql version (Ex: $0 37 mysql55)"
    exit 1
fi

docker-compose -f docker-compose-tests.yml run -v $(pwd):/home/mitzasql/src --rm -e DB_HOST="tcp://$2" "python$1" bash
