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
build: distutils-build docs

# target: clean - Remove all build and testing artifacts.
clean: clean-doc clean-pyc

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

MAN_HTML_FILES = ${MAN_MD_FILES:.md=.html}
MAN_ROFF_FILES = ${MAN_MD_FILES:.md=.roff}
MAN_MD_FILES = $(wildcard share/man/*.md)
PANDOC_VER = $(shell rpm --query --queryformat '%{VERSION}\n' pandoc \
			         | cut -c -2)
ifeq "${PANDOC_VER}" '1.'
# pandoc 1.x and earlier
PANDOC := pandoc --from markdown+auto_identifiers --smart --standalone --toc
else
# pandoc 2.x and later
PANDOC := pandoc --from markdown+auto_identifiers+smart --standalone --toc
endif
PANDOC_HTML := ${PANDOC} --to html
PANDOC_ROFF := ${PANDOC} --to man

# Project specific targets {{{1

%.roff: %.md
	${PANDOC_ROFF} $< -o $@

%.html: %.md
	${PANDOC_HTML} $< -o $@

# target: clean-doc - Remove all documentation build artifacts.
clean-doc:
	@echo Removing all documentation build artifacts...
	rm -rf share/man/*.[1-8].{html,roff}

# target: clean-pyc - Remove all Python bytecode build artifacts.
clean-pyc:
	@echo Removing all Python bytecode build artifacts...
	find . \
		\( -name '*.pyc' -type f -delete \) , \
		\( -name '__pycache__' -type d -delete \)

# target: docs - Build all documentation.
docs: docs-man

# target: docs-man - Build the man pages in roff and HTML formats.
docs-man: ${MAN_ROFF_FILES} ${MAN_HTML_FILES}

# target: distutils-build - Build the Python package using distutils.
distutils-build:
	@echo Building the Python package...
	python3 lib/${PY3_PKG_NAME}/setup.py build

# target: koji-build - Submit build RPM task into Koji.
koji-build:
	tito release all
