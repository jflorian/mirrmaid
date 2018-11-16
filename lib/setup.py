#!/usr/bin/python
# coding=utf-8

from distutils.core import setup

setup(
    name='mirrmaid',
    url='http://www.doubledog.org/trac/mirrmaid/',
    description='efficient mirror manager',
    author='John Florian',
    author_email='jflorian@doubledog.org',
    license='GPLv3+',
    packages=[
        'mirrmaid',
        'mirrmaid.logging',
    ],
    package_dir={'': 'lib'},
    requires=[
        'yaml',
    ],
    scripts=[
        'bin/mirrmaid',
    ],
    long_description="""\
This package efficiently maintains synchronized target mirrors of source
resources.  This is primarily accomplished by a sophisticated wrapper around
the venerable rsync package.  The primary advantage of this package over rsync
is the simple yet powerful configuration, automatic cron scheduling and
locking to prevent concurrently running instances from working against each
other.
""",
)
