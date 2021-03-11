#!/usr/bin/env bash

set -e

export LANG=C.UTF-8
export LC_ALL=C.UTF-8

# git clone https://github.com/spacetelescope/nbcollection nbcollection
git clone https://github.com/jbcurtin/nbcollection nbcollection
cd nbcollection
# git checkout 09473aba85a78efd4cbd7a20e21b95dc9a9131cf
pip install -U pip setuptools
pip install -r ci_requirements.txt
python setup.py install
cd -
