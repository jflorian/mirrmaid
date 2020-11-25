% MIRRMAID(1) | User Commands
<!---
SPDX-License-Identifier: GPL-3.0-or-later
Copyright 2020 John Florian

This file is part of mirrmaid.
-->
# NAME

`mirrmaid` -- efficient mirror manager

# SYNOPSIS

## Getting help

| `mirrmaid` { `-h` | `--help` }


## Basic usage

The general form is:

`mirrmaid` [*OPTIONS*]



# SYNTAX

## OPTIONS

These options are described more specifically below in the [GENERAL
OPTIONS][GENERAL OPTIONS] section.  You can see a brief summary of each with:

`mirrmaid` `--help`



# DESCRIPTION

_mirrmaid_ makes maintaining mirrors safe, easy and efficient.  It is largely
a wrapper around the venerable _rsync_(1) tool bringing these additional
features:

 * versatile configuration for declaring mirroring options, sources and targets
 * managed logging
 * parallel _rsync_ threads to maximize bandwidth
 * resource locking to ensure only one _rsync_ worker per mirror



# GENERAL OPTIONS

`-h`, `--help`

:   Show a brief summary of the command-line usage and exit.


`-c` *CONFIG_FILENAME*, `--config` *CONFIG_FILENAME*

:   Name of an alternate configuration to be used instead of the default
    _mirrmaid.conf_(5).


`-d`, `--debug`

:   Enable debug-level messages for the _mirrmaid_ command.  The debug and
    verbose options are mutually exclusive.  Both may be specified but only the
    last one on the command-line is honored.


`-v`, `--verbose`

:   Enable info-level messages for the _mirrmaid_ command.  The verbose and
    debug options are mutually exclusive.  Both may be specified but only the
    last one on the command-line is honored.



# CONFIGURATION

Unless the `-c` [option][GENERAL OPTIONS] is used, _mirrmaid_ makes use of
`/etc/mirrmaid/mirrmaid.conf`.  See _mirrmaid.conf_(5) for more details.



# EXIT STATUS

An exit status of zero means the application executed successfully.  Non-zero
values indicate various errors, which should be accompanied by an informative
message to stderr.  All exit status values can be generally described as
follows however:

 * `0`: Operation was successful.

 * `64`: The syntax of your _mirrmaid_ command could not be understood.

 * `69`: A required service or other resource is unavailable.

 * `70`: An internal software error occurred.  This almost certainly indicates
   a bug.

 * `71`: A general operating system error occurred.

 * `73`: A critical directory or file could not be created.

 * `75`: A temporary failure occurred.  Trying again may result in success.



# ENVIRONMENT

The _mirrmaid_ command makes no use of any special environment variables.


# BUGS

If you stumble upon a bug, please send an email with details to the author or
better yet, create an issue at the [project's issue
tracker](https://github.com/jflorian/mirrmaid/issues).



# SEE ALSO

 * _mirrmaid.conf_(5)
 * _rsync_(1)
