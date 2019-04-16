# About
MitzaSQL is a Python3 TUI MySQL client which aims to provide an easy to use console alternative to GUI clients. It is not meant to be a full-fledged GUI client, it only provides a read only view of the database, though you can manipulate the data by using raw SQL queries. Some of the main features are:

* Manage multiple sessions
* View databases
* View list of tables, sql views & stored procedures in a database
* View rows in a table or sql view:
* Easily sort table data
* Filter table data using VIM like commands (`:like`, `:gt`, `:lt`, `:in`...)
* SQL Query editor
* VIM style keyboard shortcuts (see the Help section in the program)
* VIM style commands with autocomplete support
* Macros support

MitzaSQL is heavily inspired by [HeidiSQL](https://github.com/HeidiSQL/HeidiSQL).

# Security
By default MitzaSQL stores connection credentials in plain text files in your home directory. If security is a concern you could store the file in an encrypted partition/directory and specify the path to the session file when the program starts using the `--sessions_file /path/to/sessions.ini` flag. Another option would be not to persist the connection credentials when creating a new session.

# Performance & known issues
Loading large datasets will slow down the rendering. By default, when opening a table screen only the first 100 records are loaded. The rest of the data is loaded on demand when scrolling down. When running queries with the SQL Query editor make sure you don't load large number of records or else your user experience might suffer.

# Dependencies
* urwid
* mysql-connector-python
* appdirs

# Installation

    pip3 install mitzasql

# Development
## Dependencies
* tox

## Run development version

    tox -e dev
    source .tox/dev/bin/activate

## Tests

    tox
