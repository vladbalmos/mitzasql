[![Build Status](https://travis-ci.com/vladbalmos/mitzasql.svg?branch=master)](https://travis-ci.com/github/vladbalmos/mitzasql)

# About
MitzaSQL is a free Python3 TUI MySQL client for Linux which aims to provide an easy-to-use console alternative to GUI clients. It is not meant to be a full-fledged GUI client, it only provides a read-only view of the database, though you can manipulate the data by using raw SQL queries. Some of the main features are:

* Manage multiple sessions
* View databases
* View list of tables, sql views & stored procedures in a database
* View rows in a table or sql view:
* Easily sort table data
* Filter table data using VIM-like commands (`:like`, `:gt`, `:lt`, `:in`...)
* SQL Query editor with syntax highlighting, **smart autocomplete** and clipboard support (optional dependency needs to be installed)
* VIM style keyboard shortcuts
* VIM style commands with autocomplete support
* Macros support

MitzaSQL is heavily inspired by [HeidiSQL](https://github.com/HeidiSQL/HeidiSQL) and is licensed under [MIT](https://opensource.org/licenses/MIT). The lexer's tokens implementation used by the auto complete system was taken from the [python-sqlparse](https://github.com/andialbrecht/sqlparse) project.

### Demo
[![asciicast](https://asciinema.org/a/fbbwVEIdL9f8UbQFtPAw2NsCl.svg)](https://asciinema.org/a/fbbwVEIdL9f8UbQFtPAw2NsCl)

# Website
[https://vladbalmos.github.io/mitzasql](https://vladbalmos.github.io/mitzasql)

# System requirements
* Linux
* Python3 (3.6 - 3.9)
* MySQL (5.6 - 8)

# Security
By default MitzaSQL stores connection credentials in plain text files in your home directory. If security is a concern you could store the file in an encrypted partition/directory and specify the path to the session file when the program starts using the `--sessions_file /path/to/sessions.ini` flag. Another option would be not to persist the connection credentials when creating a new session.

# Performance & known issues
Loading large datasets will slow down the rendering. By default, when opening a table screen only the first 100 records are loaded. The rest of the data is loaded automatically when scrolling down. When running queries with the SQL Query editor make sure you don't load a large number of records or else your user experience might suffer.

# Dependencies
* urwid
* mysql-connector-python
* appdirs
* pygments

# Installation

    pip3 install mitzasql

If you require clipboard support you need to install the extra dependency:

    pip3 install mitzasql[clipboard]

This will install the [pyperclip](https://github.com/asweigart/pyperclip) module. Keep in mind that **pyperclip** requires `xclip`/`xsel` to be installed on Linux, or the `gtk`/`qt` python modules.

# Development
## Dependencies
* tox
* Docker (optional)
* docker-compose (optional)

Docker is only required for running the integration tests, testing during feature development can be done with tox alone (see below).

## Running the development version

    # If your currently installed Python version != 3.6 use TOXENV to specify it
    tox -e dev
    source .tox/dev/bin/activate
    mitzasql

To run the program using a different Python version using Docker:

    ./run-in-docker.sh [python version] [mysql version]
    # ./run-in-docker.sh 36 mysql55
    tox -e dev
    source .tox/dev/bin/activate
    mitzasql

## Tests
The testing process uses tox & Docker to automate running the tests against multiple versions of Python and MySQL servers.

During feature development Docker is not really necessary, I use it to run the test MySQL server but it that can be installed directly on the host. If that is the case, then new connection details have to be specified using environmental variables (see `tests/db/connection_fixture.py` for more details).

To run the tests during feature development run:

    cp env.template .env # necessary if using Docker
    docker-compose up # necessary if using Docker
    tox

To generate code coverage:

    ./coverage.sh

Code coverage is generated in the `htmlcov` directory.

### Integration testing
See `test-mitzasql.sh` for more info.

### UI testing
See `test-mitzasql-ui.sh` for more info.

