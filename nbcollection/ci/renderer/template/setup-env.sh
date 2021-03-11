#!/usr/bin/env bash

set -e

export LANG=C.UTF-8
export LC_ALL=C.UTF-8

git clone https://github.com/spacetelescope/nbcollection nbcollection
cd nbcollection
git checkout 9070c5464e901f9ab4cf274f4b748abb9d6994d1
pip install -U pip setuptools
pip install -r ci_requirements.txt
python setup.py install
cd -
