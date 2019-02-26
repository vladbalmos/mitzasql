# Project goals
* minimal dependencies set
* minimal interface/UI
* KISS functionality
* easy installation through multiple channels (direct download, python package managers, snapd, Docker, flatpack)
* translations support
* unicode support
* semantic versioning

# Roadmap
## 0.1
* project setup [done]
    * directories structure [done]
    * development workflow [done]
* research curses programming [done]
* create minimal script which displays a text widget [done]

## 0.2
* research unicode handling (input & UI)
* create minimal UI framework with unicode support [done]
* create translation framework
* create the connections related functionality [done]
    * show saved connections [done]
    * create new connection [done]
    * edit connection [done]
    * delete connection [done]
    * test connection [done]
    * connect [done]
* quit functionality [done]
* cleanup widgets (remove event handlers) [done]
* make strings unicode [done]
* create docstrings & document architecture [done]
* cleanup the theme [done]
* config & sessions list location (don't hardcode it) [done]

## 0.3
* create & test Docker image
* create & test pip installed package
* installation guides for each supported method
* show server view (list of databases) [done]
* show connection info [won't implement]
* create database dialog [done]
* drop database [done]

## 1.0.0
* improve theming

# Development
## Required tools:
* tox

## Running the environment
tox -e dev
source .tox/dev/bin/active

## Running the tests
tox
