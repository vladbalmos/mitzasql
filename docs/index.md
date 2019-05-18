---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
---

[![Build Status](https://travis-ci.org/vladbalmos/mitzasql.svg?branch=master)](https://travis-ci.org/vladbalmos/mitzasql)

## About

MitzaSQL is a free Python3 TUI MySQL client for Linux which aims to provide an easy-to-use console alternative to GUI clients. It is not meant to be a full-fledged GUI client, it only provides a read-only view of the database, though you can manipulate the data by using raw SQL queries. Some of the main features are:

* Manage multiple sessions
* View databases
* View list of tables, sql views & stored procedures in a database
* View rows in a table or sql view:
* Easily sort table data
* Filter table data using VIM-like commands (`:like`, `:gt`, `:lt`, `:in`...)
* SQL Query editor
* VIM style keyboard shortcuts
* VIM style commands with autocomplete support
* Macros support

MitzaSQL is heavily inspired by [HeidiSQL](https://github.com/HeidiSQL/HeidiSQL) and its licensed under [MIT](https://opensource.org/licenses/MIT).  
Demo and screenshots are available [here]({{ "/screenshots" | relative_url }}).

## Project goals
- Minimal dependencies
- Ease of use
- **No mouse support**

## Serving suggestion
Best served with `tmux` and `vim`.

## Windows & MacOS ports
To run `MitzaSQL` on Windows/MacOS build a Docker image and run it inside a container. Use the project's [Dockerfile](https://github.com/vladbalmos/mitzasql/blob/master/Dockerfile) as a starting point. An official Docker image is coming soon.

## Planned features
- Support SSL connections
- Query log
- Autocomplete support and syntax highlighting for the SQL editor
- Persist column sizes settings between sessions
- Official Docker image

## Known issues
See the github project page, section [Performance and known issues](https://github.com/vladbalmos/mitzasql#performance--known-issues).

## Security
See the github project page, section [Security](https://github.com/vladbalmos/mitzasql#security).

## Bugs
Please report any bugs here: [https://github.com/vladbalmos/mitzasql/issues](https://github.com/vladbalmos/mitzasql/issues).

## Author
<a href="https://github.com/vladbalmos"><span class="icon icon--github">{% include icon-github.svg %}</span><span class="username">Vlad Balmos</span></a>
