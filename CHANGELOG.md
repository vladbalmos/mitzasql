# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
