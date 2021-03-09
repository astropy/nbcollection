#!/usr/bin/env bash

set -e

export LANG=C.UTF-8
export LC_ALL=C.UTF-8

git clone https://github.com/spacetelescope/nbcollection nbcollection
cd nbcollection
git checkout 5b8f443af1509aa3c0d50115e5efae80d30841ff
pip install -U pip setuptools
pip install -r ci_requirements.txt
python setup.py install
cd -
