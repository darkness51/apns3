# Project settings
PROJECT := apns3
PACKAGE := apns
SOURCES := Makefile setup.py $(shell find $(PACKAGE) -name '*.py')
HOOKS := $(shell find .githooks/)

# Python settings
ifndef TRAVIS
	ifndef PYTHON_MAJOR
		PYTHON_MAJOR := 3
	endif
	ifndef PYTHON_MINOR
		PYTHON_MINOR := 5
	endif
	ENV := env/py$(PYTHON_MAJOR)$(PYTHON_MINOR)
else
	# Use the virtualenv provided by Travis
	ENV = $(VIRTUAL_ENV)
endif

# System paths
OPEN := open
SYS_PYTHON := python$(PYTHON_MAJOR).$(PYTHON_MINOR)

# Virtual environment paths
BIN := $(ENV)/bin
ACTIVATE := . $(BIN)/activate

# Virtual environment executables
PYTHON := $(BIN)/python
PIP := $(BIN)/pip
EASY_INSTALL := $(BIN)/easy_install
RST2HTML := $(PYTHON) $(BIN)/rst2html.py
PDOC := $(PYTHON) $(BIN)/pdoc
MKDOCS := $(BIN)/mkdocs
PEP8 := $(BIN)/pep8
FLAKE8 := $(BIN)/flake8
PEP257 := $(BIN)/pep257
PYLINT := $(BIN)/pylint
PYTEST := $(BIN)/py.test
COVERAGE := $(BIN)/coverage

# Flags for PHONY targets
DEPENDS := $(ENV)/.depends
HOOKS_INSTALLED := .git/hooks/.installed

REQS_DIR := requirements
REQS := $(REQS_DIR)/base.txt
OSSL_REQS := $(REQS_DIR)/pyopenssl.txt
DEV_REQS := $(REQS_DIR)/dev.txt


# Main Targets ###############################################################

.PHONY: all
all: test

# Development Installation ###################################################

.PHONY: env
env: $(PIP)

$(PIP):
	virtualenv --python $(SYS_PYTHON) $(ENV)
	$(PIP) install wheel

.PHONY: depends
depends: env Makefile $(DEPENDS) $(HOOKS_INSTALLED)
$(DEPENDS): Makefile $(DEV_REQS) $(REQS)
	$(PIP) install -e .[pyopenssl]
	$(PIP) install -r $(DEV_REQS)
	touch $(DEPENDS)  # flag to indicate dependencies are installed

$(HOOKS_INSTALLED): $(HOOKS)
	./hooker.sh --install
	touch $(HOOKS_INSTALLED)

# Documentation ##############################################################

%.rst: %.md
	pandoc -f markdown_github -t rst -o $@ $<

.PHONY: verify-readme
verify-readme: $(DOCS_FLAG)
$(DOCS_FLAG): README.rst CHANGES.rst
	$(PYTHON) setup.py check --restructuredtext --strict --metadata
	@ touch $(DOCS_FLAG)  # flag to indicate README has been checked

.PHONY: doc
doc: README.rst verify-readme sphinx-docs

.PHONY: sphinx-docs
sphinx-docs: depends
	$(ACTIVATE); cd docs; $(MAKE) html

.PHONY: read
read: doc
	$(OPEN) docs/build/html/index.html

# Static Analysis ############################################################

.PHONY: check
check: flake8 pep257

NO_PEP8 := E731

.PHONY: flake8
flake8: depends
	$(FLAKE8) $(PACKAGE) tests --ignore=$(NO_PEP8)

NO_PEP257 := D100,D101,D102,D103,D104,D105

.PHONY: pep257
pep257: depends
	$(PEP257) $(PACKAGE) --ignore=$(NO_PEP257)

.PHONY: pylint
pylint: depends
	$(PYLINT) $(PACKAGE) tests --rcfile=.pylintrc

# Testing ####################################################################

PYTEST_CORE_OPTS := tests
PYTEST_COV_OPTS :=    \
	--cov=$(PACKAGE)  \
	--no-cov-on-fail  \
	--cov-report=html \
	--cov-report=term-missing

PYTEST_OPTS := $(PYTEST_CORE_OPTS) $(PYTEST_COV_OPTS)

.PHONY: test
test: depends
	$(PYTEST) $(PYTEST_OPTS)

test-all: test-py27 test-py34 test-py35
test-py27:
	PYTHON_MAJOR=2 PYTHON_MINOR=7 $(MAKE) test
test-py34:
	PYTHON_MAJOR=3 PYTHON_MINOR=4 $(MAKE) test
test-py35:
	PYTHON_MAJOR=3 PYTHON_MINOR=5 $(MAKE) test

.PHONY: htmlcov
htmlcov:
	$(OPEN) htmlcov/index.html

# Cleanup ######################################################################

.PHONY: clean
clean: .clean-dist .clean-test .clean-doc .clean-build

.PHONY: clean-all
clean-all: clean .clean-env

.PHONY: .clean-build
.clean-build:
	find $(PACKAGE) tests -name '*.pyc' -delete
	find $(PACKAGE) tests -name '__pycache__' -delete
	rm -rf *.egg-info

.PHONY: clean-doc
clean-doc:
	rm -rf README.rst docs/build

.PHONY: .clean-test
.clean-test:
	rm -rf .pytest .coverage htmlcov

.PHONY: .clean-dist
.clean-dist:
	rm -rf dist build

.PHONY: .clean-env
.clean-env: clean
	rm -rf env

# Release ######################################################################

.PHONY: register-test
register-test: doc
	$(PYTHON) setup.py register --strict --repository https://testpypi.python.org/pypi

.PHONY: upload-test
upload-test: register-test
	$(PYTHON) setup.py sdist upload --repository https://testpypi.python.org/pypi
	$(PYTHON) setup.py bdist_wheel upload --repository https://testpypi.python.org/pypi
	$(OPEN) https://testpypi.python.org/pypi/$(PROJECT)

.PHONY: register
register: doc
	$(PYTHON) setup.py register --strict

.PHONY: upload
upload: .git-no-changes register
	$(PYTHON) setup.py sdist upload
	$(PYTHON) setup.py bdist_wheel upload
	$(OPEN) https://pypi.python.org/pypi/$(PROJECT)

.PHONY: .git-no-changes
.git-no-changes:
	@ if git diff --name-only --exit-code;        \
	then                                          \
		echo Git working copy is clean...;        \
	else                                          \
		echo ERROR: Git working copy is dirty!;   \
		echo Commit your changes and try again.;  \
		exit -1;                                  \
	fi;
