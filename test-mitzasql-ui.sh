#!/bin/bash

# This is mostly smoke testing. It runs a series a ui macros
# using dockerized python versions to ensure that no unhandled
# exceptions are raised

if [ ! -f .env ]; then
    echo 'Missing .env file'
    exit 1
fi

if [ "$1" = 'help' ]; then
    echo "Usage: $0 [mysql56|mysql57|mysql8] [py36|py37|py38|py39]"
    exit 0
fi

# Download database fixtures
./download-db-fixtures.sh || exit 1

if [ -z "$1" ]; then
    mysql_services='mysql56 mysql57 mysql8'
else
    mysql_services="$1"
fi

if [ -z "$2" ]; then
    python_versions='py36 py37 py38 py39'
else
    python_versions="$2"
fi

python_services=''
for py in $python_versions; do
    service_name="python${py/py/}"
    python_services="${python_services} $service_name"
done

FILE=docker-compose-tests.yml
echo 'Building images...'
docker-compose -f "$FILE" build $python_services
docker-compose -f $FILE up -d $mysql_services

# Wait for all mysql containers to finish initialization
sleep 5
for version in $mysql_services; do
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
    for my in $mysql_services; do
        echo "$py - $my"
        service_name="python${py/py/}"
        docker-compose -f $FILE run --rm -e TRAVIS_JOB_ID="$TRAVIS_JOB_ID" -e TRAVIS_BRANCH="$TRAVIS_BRANCH" -e DB_HOST='tcp://'$my $service_name \
            bash -c "source .tox/$py/bin/activate && \
            cd tests/macros && \
            coverage run run.py && coveralls" || exit 1
    done
done

docker-compose -f $FILE stop
