<!--
SPDX-License-Identifier: GPL-3.0-or-later
Copyright 2020 John Florian <jflorian@doubledog.org>

This file is part of mirrmaid.
-->
# mirrmaid - efficient mirror manager

_mirrmaid_ makes maintaining mirrors safe, easy and efficient.  It is largely
a wrapper around the venerable _rsync_(1) tool bringing these additional
features:

 * versatile configuration for declaring mirroring options, sources and targets
 * managed logging
 * parallel _rsync_ threads to maximize bandwidth
 * resource locking to ensure only one _rsync_ worker per mirror
