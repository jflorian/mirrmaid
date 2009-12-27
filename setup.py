#!/usr/bin/env python

from distutils.core import setup


if __name__ == "__main__":
    setup(
        name="doubledog_mirror_manager",
        url="http://mdct-00fs/cgi-bin/cvsweb.cgi/mdct-tools/doubledog-mirror-manager/",
        description="PICAPS remote archive collection agent for localized backups",
        author="John Florian",
        author_email="jflorian@doubledog.org",
        license="Dart Container Corp. Proprietary",
        packages=["doubledog_mirror_manager"],
        long_description="""
Collects PICAPS archives from various servers for inclusion in a local Bacula backup.
""",
    )
