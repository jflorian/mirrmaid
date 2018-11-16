# vim: foldmethod=marker

# Standard spec file parsing {{{1

SPECFILE = $(firstword $(wildcard *.spec))

# If there are sub-packages, assume the first is appropriate in forming NVR.
# The dist macro is defined as a null string because it's normal value is
# unwanted in these query results.
queryspec = $(shell rpm --query --queryformat "%{$(1)}\n" \
							--define="dist %{nil}" \
							--specfile $(SPECFILE) \
					| head --lines=1)

NAME := $(call queryspec,NAME)
VERSION := $(call queryspec,VERSION)
RELEASE := $(call queryspec,RELEASE)

# The treeish we'll archive is effectively the Git tag that tito created.
TREEISH := ${NAME}-${VERSION}-${RELEASE}

# Standard targets {{{1

# target: help - Show all callable targets.
help:
	@grep -P '^#\s*target:\s*' Makefile | sort

# target: build - Build the package.
build: distutils-build

# target: clean - Remove all build and testing artifacts.
clean: clean-pyc

# target: dist - Produce a build for distribution.
dist: koji-build

# target: sources - Produce all forms of source distribution.
sources: tarball

# target: tarball - Produce tarball of source distribution.
tarball:
	git archive \
		--output=${NAME}-${VERSION}.tar.gz \
		--prefix=${NAME}-${VERSION}/ \
		${TREEISH}

# Project specific variables {{{1

PY3_PKG_NAME := ${NAME}
export PYTHONPATH=lib
# Project specific targets {{{1

# target: clean-pyc - Remove all Python bytecode build artifacts.
clean-pyc:
	@echo Removing all Python bytecode build artifacts...
	find . \
		\( -name '*.pyc' -type f -delete \) , \
		\( -name '__pycache__' -type d -delete \)

# target: distutils-build - Build the Python package using distutils.
distutils-build:
	@echo Building the Python package...
	python3 lib/${PY3_PKG_NAME}/setup.py build

# target: koji-build - Submit build RPM task into Koji.
koji-build:
	tito release all
