#!/bin/bash
if [ -d tests/db_fixtures ]; then
    echo "Database fixtures exist."
fi

echo 'Downloading database fixtures...'
wget -O tests/db_fixtures.tar.gz 'https://s3.amazonaws.com/mitzasql/db_fixtures.tar.gz' || exit 1
cd tests && tar -xvf db_fixtures.tar.gz || exit 1
rm -f db_fixtures.tar.gz
