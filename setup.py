import os
import sys

from setuptools import find_packages, setup

# Always reference code-origin
# https://github.com/django/django/blob/master/setup.py#L7

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 7)
ENCODING = 'utf-8'

if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write("""
==========================
Unsupported Python version
==========================
This version of docker-ops requires Python {}.{}, but you're trying to
install it on Python {}.{}.
This may be because you are using a version of pip that doesn't
understand the python_requires classifier. Make sure you
have pip >= 9.0 and setuptools >= 24.2, then try again:
    $ python -m pip install --upgrade pip setuptools
    $ python -m pip install bert
This will install the latest version of docker-ops which works on your
version of Python
""".format(*(REQUIRED_PYTHON + CURRENT_PYTHON)))
    sys.exit(1)


EXCLUDE_FROM_PACKAGES = []
version = '0.0.2'

INSTALL_REQUIRES = [
    'GitPython==3.1.1',
    'Jinja2==2.11.2',
    'jupyter-client==6.1.3',
    'nbconvert==5.6.1',
    'requests==2.23.0',
    'toml==0.10.1',
    'PyYAML==5.3.1',
    'lxml==4.6.2',
    'beautifulsoup4==4.9.3',
]

description = 'Execute and convert collections of Jupyter notebooks to static HTML'

def read(fname):
  with open(os.path.join(os.path.dirname(__file__), fname)) as f:
    return f.read()

setup(
    name='nbcollection',
    version=version,
    python_requires='>={}.{}'.format(*REQUIRED_PYTHON),
    url='https://github.com/astropy/nbcollection',
    author="Joe Curtin <jcurtin@stsci.edu",
    author_email='jcurtin@stsci.edu',
    description=description,
    long_description=read('README.md'),
    license='MIT',
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    scripts=[],
    install_requires=INSTALL_REQUIRES,
    entry_points={'console_scripts': [
        'nbcollection = nbcollection.__main__:main',
        'nbcollection-ci = nbcollection.ci.__main__:run_from_cli',
    ]},
    zip_safe=False,
    classifiers=[
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3 :: Only',
  ],
  project_urls={}
)
