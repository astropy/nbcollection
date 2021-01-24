#!/usr/bin/env bash

# This file is used quicken common manual routines. At somepoint it needs to be ported to python/pytest after we decide
#  which CI/CD we should us.
#  https://github.com/astropy/nbcollection/issues/2

set -e
# set -x
if [ "$1" == "docs" ]; then
    if [ ! -d "env-docs" ]; then
        virtualenv -p $(which python3) env-docs
        source env-docs/bin/activate
        pip install sphinx sphinx_rtd_theme -U
    else
        source env-docs/bin/activate
    fi
    mkdir -p /tmp/docs
    sphinx-build -b html docs/ /tmp/docs/
fi

if [ "$1" == "run-tests" ]; then
    if [ ! -d "env-tests" ]; then
        virtualenv -p $(which python3) env-tests
        source env-tests/bin/activate
        pip install -r ci_requirements.txt
        pip install pytest
    else
        source env-tests/bin/activate
    fi
    # AUTH_PASSWORD=... AUTH_USERNAME=...
    PYTHONPATH='.' pytest nbcollection_tests/ci/test_generator.py
fi

if [ "$1" == "reset-test-repo" ]; then
    rm -rf /tmp/jdat_notebooks || true
    git clone git@github.com:jbcurtin/nbcollection-notebook-test-repo.git /tmp/jdat_notebooks
    cd /tmp/jdat_notebooks
    git remote add jbcurtin git@github.com:jbcurtin/jdat_notebooks.git
    # git remote set-url --delete origin git@github.com:jbcurtin/nbcollection-notebook-test-repo.git
    git remote add jbcurtin-test git@github.com:jbcurtin/nbcollection-notebook-test-repo.git
    git fetch --all
    git reset jbcurtin-test/master --hard
    git push jbcurtin master --force
    cd -
fi
