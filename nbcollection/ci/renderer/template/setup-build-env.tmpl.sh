#!/usr/bin/env python

set -e
cd {{ build_context.build_dir }}
virtualenv -p $(which python) venv
source venv/bin/activate

pip install -U pip setuptools --use-feature=2020-resolver
if [ -f "pre-install.sh" ]; then
    bash pre-install.sh
fi
if [ -f "pre-requirements.txt" ]; then
    pip install -U -r requirements.txt
fi
pip install -U -r requirements.txt
if [ -f "environment.sh" ]; then
    source environment.sh
fi
if ! pip freeze |grep 'jupyter==' >/dev/null 2>/dev/null; then
    pip install -U jupyter --use-feature=2020-resolver
fi
cd -
exit 0
