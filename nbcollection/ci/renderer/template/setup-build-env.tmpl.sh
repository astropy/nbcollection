#!/usr/bin/env python

set -e
cd {{ build_context.build_dir }}
python -m venv .
source bin/activate
pip install -U GitPython==3.1.1 Jinja2==2.11.2 nbconvert==5.6.1 requests==2.23.0 toml==0.10.1

pip install -U pip setuptools wheel
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
    pip install -U jupyter
fi
if ! pip freeze |grep 'jupyter-client==' >/dev/null 2>/dev/null; then
    jupyter-client==6.1.3
fi
cd -
exit 0
