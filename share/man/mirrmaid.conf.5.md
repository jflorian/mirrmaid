%MIRRMAID.CONF(5) | File Formats
<!---
SPDX-License-Identifier: GPL-3.0-or-later
Copyright 2018-2020 John Florian

This file is part of mirrmaid.
-->
# NAME

`/etc/mirrmaid/mirrmaid.conf` -- _mirrmaid_ configuration file



# DESCRIPTION

This file or one like it can be used to configure various parameters of the
_mirrmaid_ application.  You may want several, depending on your use-case.  For
example, it's common to have one for each Linux distribution you mirror.


## Format

In general, the file content consists of sections, started by a `[`*SECTION*`]`
header, followed by configuration options which take one of the following
interchangeable forms:

| *NAME* `:` *VALUE*
| *NAME* `=` *VALUE*

*NAME* should be one of those documented in [OPTIONS][].  All other names will
be ignored.

*VALUE* may span multiple lines, provided they are indented deeper than the
first line of the *VALUE* setting.   Leading and trailing white-space is
ignored for both *NAME* and *VALUE*.


### Comments

Comments, which are ignored, begin with a hash symbol (`#`) or semi-colon (`;`)
and continue to the end of the line.  Comments must appear on their own line
that would otherwise be an empty line.  They may be indented however, if
desired.


### Interpolation

The configuration parser supports interpolated values.   It enables values to
contain format strings which refer to other values in the same section, or
values in the special `[DEFAULT]` section.  For example, a *VALUE* of `Spam is
not just for %(meal)s anymore` would result in `Spam is not just for fine
dining excursions anymore` if the same section (or the `[DEFAULT]` section)
contained `meal: fine dining excursions`.  Consequently this means the percent
symbol (`%`) has magic associated with it.  To get a regular percent symbol you
need to use two consecutive percent symbols as a way to escape the
interpolation, e.g., `max=100%%`.



# OPTIONS

Options are organized into sections, started by a `[`*SECTION*`]` header.
Valid section names are as follows: `[DEFAULT]`, `[MIRRMAID]`, and `[MIRRORS]`.
In addition to those fixed section names, you must also have one section for
each named mirror.  Each section is described in more detail below.  Any other
sections will be ignored.

While this man page refers to these categorically as options so as to conform
with common man page conventions, some of these parameters are strictly
required and not optional at all.  To minimize confusion, each is labeled
clearly as required or optional.


## [DEFAULT] SECTION

This section is mostly only used for the [INTERPOLATION][] feature described
above.  However, it does have one required setting (below).


`rsync_options` (required)

:   The general options to be passed to _rsync_ while maintaining any of the
    mirrors described in the `[MIRRORS]` section.  Note that order can be
    important, as some options may override some or all of others.  For
    example, you may wish to use `--archive` to conveniently set a number of
    options implicitly and follow that with `--no-group` and `--no-owner` to
    let _mirrmaid_ own the files in your mirror.

    This must be expressed as a valid Python list.  E.g., `['--archive',
    '--no-group', '--no-owner']`.  The example configuration file provides
    a reasonable set to get you started.


## [MIRRMAID] SECTION

The following options are recognized within the `[MIRRMAID]` section.  These
control how this _mirrmaid_ behaves while maintaining any of the mirrors
described in the `[MIRRORS]` section.


`max_workers` (optional)

:   Limits the number of concurrent _rsync_ processes that each instance of
    _mirrmaid_ will start.  Keep in mind that this number may be exceeded if
    more than one instance of _mirrmaid_ is running concurrently.  A minimum
    value of one is silently enforced.

    The default is 2.


`proxy` (optional)

:   If set, this takes the form of *PROXY_HOST*`:`*PROXY_PORT*.  *PROXY_HOST*
    must permit outbound proxy connections to TCP port 873 (IANA standard
    _rsync_) for this to work.

    The default is `` (an empty string) so as to not use a proxy.


`summary_group` (optional)

:   If you have multiple mirrmaid configurations/jobs established on a single
    host, you may wish to keep the operations summaries distinct for each.  Each
    `summary_group` will result in a distinct operations summary and may be
    shared among any number of configurations/jobs, if desired.  The value of
    `summary_group` can be anything you wish.

    The default is `My Mirrors`

    It will be included in the email subject like so:

        mirrmaid Activity Summary for My Mirrors


`summary_history_count` (optional)

:   The number of historical copies of operational summaries that _mirrmaid_ is
    to retain on disk before they are rotated out of existence.  A minimum
    value of one is silently enforced.

    The default is `3`.


`summary_interval` (optional)

:   The minimum number of seconds that mirrmaid will wait after sending an
    operations summary via email before sending another.  A minimum value of
    ten minutes is silently enforced.

    The default is `86400` (or 24 hours).


`summary_recipients` (optional)

:   A list of email addresses to whom the operations summaries should be sent.
    If set, this must be expressed as a valid Python list.

    The default is `['root']`.


`summary_size` (optional)

:   A threshold that if the size (in bytes) of the operations summary has
    exceeded, causes the email to be sent early without necessarily waiting for
    the `summary_interval` to have elapsed.  This can be useful to alert the
    `summary_recipients` of major trouble in a more expedient way due to overly
    verbose activity.  Set this to zero to defeat this feature.

    The default is `20000`.


## [MIRRORS] SECTION

The following options are recognized within the `[MIRRORS]` section.  This is
where you get specific about what you want mirrored.


`enabled` (required)

:   Names of mirrors to be managed.  Each named mirror requires its own named
    section with details for that mirror.  Mirrors will be synchronized in the
    order listed here.  This must be expressed as a valid Python list.  E.g.,
    `['fedora-updates', 'fedora-releases']`.

    If you wish to temporarily disable a mirror, just remove it from the list
    here and leave the corresponding named mirror section intact.


## NAMED MIRROR SECTIONS

For each mirror named in `enabled` of the `[MIRRORS]` section, you must have one section declared containing all of the required settings described below.


`source`

:   The _rsync_ URI of what is to be mirrored.


`target`

:   The _rsync_ URI of where the mirror is to be kept.


`include`

:   A Python list of patterns to be included in the mirror.


`exclude`

:   A Python list of patterns to be excluded from the mirror.



# FILES

`/etc/mirrmaid/mirrmaid.conf`



# SEE ALSO

* _rsync_(1)
* _mirrmaid_(1)
