#!/usr/bin/env bash

set -e

export LANG=C.UTF-8
export LC_ALL=C.UTF-8

git clone https://github.com/spacetelescope/nbcollection nbcollection
cd nbcollection
git checkout 35094e45b6532313321b7de6fd333ac323e2211e
pip install -U pip setuptools
pip install -r ci_requirements.txt
python setup.py install
cd -
