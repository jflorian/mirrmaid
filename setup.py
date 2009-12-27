#!/usr/bin/env python

from distutils.core import setup


if __name__ == "__main__":
    setup(
        name="doubledog_mirror_manager",
        url="http://www.doubledog.org/trac/doubledog-mirror-manager/",
        description="doubledog.org local mirror manager",
        author="John Florian",
        author_email="jflorian@doubledog.org",
        license="GPLv3+",
        packages=["doubledog_mirror_manager"],
        long_description="""
This package efficiently maintains synchronized local mirrors of remote
resources.  This is primarly accomplished by a sophisticated wrapper around
the venerable rsync package.
""",
    )
