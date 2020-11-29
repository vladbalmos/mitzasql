#!/bin/bash

# This is mostly smoke testing. It runs a series a ui macros
# using dockerized python versions to ensure that no unhandled
# exceptions are raised

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

if [ -z "$1" ]; then
    mysql_versions='mysql56 mysql57 mysql8'
else
    mysql_versions="$1"
fi

if [ -z "$2" ]; then
    python_versions='py36 py37 py38 py39'
else
    python_versions="$2"
fi


# Wait for all mysql containers to finish initialization
sleep 5
for version in $mysql_versions; do
    name=$(docker-compose -f $FILE ps -q $version)
    status=$(docker inspect --format='{{.State.Health}}' $name | grep -o healthy)

    while [ "$status" != "healthy" ]; do
        status=$(docker inspect --format='{{.State.Health}}' $name | grep -o healthy)
        echo "$version server status is: $status"
        sleep 1
    done
done

echo 'All done! Running tests...'

for py in $python_versions; do
    for my in $mysql_versions; do
        echo "$py - $my"
        service_name="python${py/py/}"
        docker-compose -f $FILE run --rm -e DB_HOST='tcp://'$my $service_name \
            bash -c "source .tox/$py/bin/activate && \
            cd tests/macros && \
            ./run.py" || exit 1
    done
done

docker-compose -f $FILE stop
