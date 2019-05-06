#!/bin/bash

if [ ! -f .env ]; then
    echo 'Missing .env file'
    exit 1
fi

# Download database fixtures
./download-db-fixtures.sh || exit 1

echo 'Building images...'
FILE=docker-compose-tests.yml
docker-compose -f $FILE build
docker-compose -f $FILE up -d

# Wait for all mysql containers to finish initialization
sleep 5
for version in mysql55 mysql56 mysql57 mysql8; do
    name=$(docker-compose -f $FILE ps -q $version)
    status=$(docker inspect --format='{{.State.Health}}' $name | grep -o healthy)

    while [ "$status" != "healthy" ]; do
        status=$(docker inspect --format='{{.State.Health}}' $name | grep -o healthy)
        echo "$version server status is: $status"
        sleep 1
    done
done

echo 'All done! Running tests...'

TEST_COMMAND='tox -e py35 --notest && source .tox/py35/bin/activate && mitzasql'

docker-compose -f $FILE stop
