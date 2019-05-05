#!/bin/sh

VERSION=$(git describe)

echo "__version__ = '$VERSION'" > mitzasql/version.py
echo "Changed version"
cat mitzasql/version.py
