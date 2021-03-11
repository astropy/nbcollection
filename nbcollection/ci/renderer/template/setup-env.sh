#!/usr/bin/env bash

set -e

export LANG=C.UTF-8
export LC_ALL=C.UTF-8

git clone https://github.com/spacetelescope/nbcollection nbcollection
cd nbcollection
git checkout d56de2876b4ab4814838250007a9cc862cd3bd1d
pip install -U pip setuptools
pip install -r ci_requirements.txt
python setup.py install
cd -
