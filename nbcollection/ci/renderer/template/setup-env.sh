#!/usr/bin/env bash

set -e

export LANG=C.UTF-8
export LC_ALL=C.UTF-8

git clone https://github.com/spacetelescope/nbcollection nbcollection
cd nbcollection
git checkout 3d26c1536563427cc7235b9f6e0b2173413e3d19
pip install -U pip setuptools
pip install -r ci_requirements.txt
python setup.py install
cd -
