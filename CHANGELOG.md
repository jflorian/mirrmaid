<!--
SPDX-License-Identifier: GPL-3.0-or-later
Copyright 2020 John Florian <jflorian@doubledog.org>

This file is part of mirrmaid.
-->


# Change Log

All notable changes to this project (since v0.25.1) will be documented in this file.  This project adheres to [Semantic Versioning](http://semver.org/) since v0.25.1.  This file adheres to [good change log principles](http://keepachangelog.com/).

<!-- Template

## [VERSION] WIP
### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security

-->

## [0.26.0] 2020-12-03
### Added
- `mirrmaid.synchronizer.Synchronizer.stop` method
- `mirrmaid.manager.MirrorManager._config_signal_handler` method
- `mirrmaid.exceptions.MirrmaidRootException` class
- `mirrmaid.exceptions.SignalException` class
- `mirrmaid.synchronizer.Synchronizer.is_running` property
- `max_workers` configuration option to limit concurrency
- `mirrmaid.cli` module
- `mirrmaid.cli.MirrmaidCLI` class
- `mirrmaid`(1) man page
- bash-completion facilities
- `mirrmaid.synchronizer.Synchronizer.dry_run` parameter/property
- `--dry-run` (`-n`) option for direct pass-thru to `rsync`
- `mirrmaid.exceptions.MirrmaidRuntimeException` class
### Changed
- `mirrmaid.manager.MirrorManager` now catches signals to bring about graceful shutdowns
- `mirrmaid.exceptions.SynchronizerException` now subclasses `MirrmaidRootException`
- exit/fail more gracefully when dropping privileges if user or group are undefined
### Fixed
- `rsync` subprocesses often left running after `mirrmaid` is stopped/killed
- some failures could result in duplicate messages

## [0.25.1] 2018-11-19
This and prior versions predate this Change Log.  Please see the Git log.
