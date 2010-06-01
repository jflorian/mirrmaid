#!/usr/bin/env python

from distutils.core import setup


if __name__ == "__main__":
    setup(
        name="mirrmaid",
        url="http://www.doubledog.org/trac/mirrmaid/",
        description="efficient mirror manager",
        author="John Florian",
        author_email="jflorian@doubledog.org",
        license="GPLv3+",
        packages=["mirrmaid"],
        long_description="""
This package efficiently maintains synchronized local mirrors of remote
resources.  This is primarly accomplished by a sophisticated wrapper around
the venerable rsync package.  The primary advantage of this package over rsync
is the simple yet powerful configuration, automatic cron scheduling and
locking to prevent concurrently running instances from working against each
other.
""",
    )
