# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.3.0]

### Changed
- Switch to RawConfigParser to fix issue with percent sign in passwords (pull/86 by oliverseal)
- Drop support for Python 3.5
- Drop support for MySQL 5.5
- Upgrade to Urwid 2.1.2
- Upgrade mysql-connector-python to 8.0.22
- Upgrade appdirs to 1.4.4
- Upgrade pygments to 2.7.2
- Update documentation
- Go back to previous screen after dismissing a SQL error
- Log line numbers executed by macros
- Go back and refresh previous screen if the Query Editor runs sql which modifies records (insert, update, delete, etc...)
- Prevent caching custom queries

### Fixed
- Fix for #88: Database names with dashes cause error 1064 (42000)
- Fix for #84
- Fix for #85
- Fix for #86

## [1.2.0]

### Added
- Enable syntax highligting in the query editor (#30)
- Add command line option to disable logging (#80)
- Persist column widths across restarts (#53)
- Add :clearcache command to clear cache files

## [1.1.0]

### Added
- Add query log widget (#32)
- Add keyboard shortcuts to resize the query editor (#40)

### Changed
- Document test macros

### Fixed
- Prevent binding the "show help" signal handler multiple times
- Fix for #54: Rewrite the "session select". Replace the FSM with a signal/callback approach
- Fix for #63: Don't overwrite previous sessions while editing
- Fix issue with docker-compose network subnets

## [1.0.1]

### Added
- Add :between, :nbetween filter command

### Changed
- Add explicit dependencies to requirements.txt
- Update user manual

### Fixed
- Fix for #65: Catch exit key in info widgets
- Fix `end` key scrolling issue (#75)
- Fix connect using command line arguments bug
