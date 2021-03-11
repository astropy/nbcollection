#!/usr/bin/env bash

set -e

export LANG=C.UTF-8
export LC_ALL=C.UTF-8

git clone https://github.com/spacetelescope/nbcollection nbcollection
cd nbcollection
git checkout e6c69ed35b6ebaf04e8f110a3152093773f0c5f5
pip install -U pip setuptools
pip install -r ci_requirements.txt
python setup.py install
cd -
