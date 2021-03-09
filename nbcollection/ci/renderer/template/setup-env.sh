#!/usr/bin/env bash

set -e

export LANG=C.UTF-8
export LC_ALL=C.UTF-8

git clone https://github.com/spacetelescope/nbcollection nbcollection
cd nbcollection
git checkout ea33b6a72b55859da45728f79ebddc8975205f6d
pip install -U pip setuptools
pip install -r ci_requirements.txt
python setup.py install
cd -
