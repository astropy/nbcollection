nbcollection-ci Overview
########################

nbcollection-ci provides a collection of commands to manage Jupyter Notebook build machinery. It aims to monitor and
manage repositories at scale so the build engineer may provide a seemless experiance for the Scientific Reviewers

License
-------

Folder Structure
----------------

`nbcollection-ci` assumes a `notebooks`_ folder exists in the root level of the repository. The folder layout of
`notebooks` implements expectations set fourth by `nbcollection`_. An example of this implementation can be found
in `nbcollection-notebook-test-repo`_

.. _nbcollection-notebook-test-repo: https://github.com/jbcurtin/nbcollection-notebook-test-repo
.. _notebooks: https://github.com/jbcurtin/nbcollection-notebook-test-repo/tree/master/notebooks
.. _nbcollection: ../nbcollection/index.html#converting-a-directory-structure-of-specific-notebook-files

Example usage
-------------

Environment
+++++++++++

A thorough text-based interface was designed to provide very verbose feedback with integrating the software. Don't
be afaird to make mistakes, but remember to test this software thoroughly before implementing it in a production
repository. `nbcollection-ci` is takes care to while installing code into repositories locally or on Github

Setup
+++++

To interface with Github, create a `Personal Access Token`_ and add it to your shell environment. When creating the 
Github Personal Access Token, add the following permissions

* repo: required for general operations. Installing and Uninstalling the tool
* repo_delete: <optional> required for running tests

.. code-block:: bash

    $ export GITHUB_USER=jbcurtin
    $ export GITHUB_TOKEN=<personal-access-token>

.. _Personal Access Token: https://github.com/settings/tokens

Install
+++++++

`nbcollection-ci install` accepts an enum `--ci-type` and string `--repo-path`. 

.. code-block:: python

    $ pip install nbcollection -U
    $ nbcollection-ci install -h
      usage: nbcollection-ci install [-h] -t CI_TYPE -r REPO_PATH [-o]
      
      Install Astropy Jupyter notebook build machinery into a Source-Code Repository
      
      optional arguments:
        -h, --help            show this help message and exit
        -t CI_TYPE, --ci-type CI_TYPE
                              Supported CI-Types: [circle-ci, github-actions]
        -r REPO_PATH, --repo-path REPO_PATH
                              Local or remote path to repo to be installed
        -o, --overwrite       Overwrite CI-Solution in local or remote path
      
      Example Usage:
      
          Install machinery locally:
          nbcollection-ci install --ci-type circle-ci --repo-path /tmp/my-new-repository
      
          Install build machinery remotely:
          nbcollection-ci install --ci-type circle-ci --repo-path https://github.com/jbcurtin/notebooks


Uninstall
+++++++++

.. code-block:: python

    $ pip install nbcollection -U
    $ nbcollection-ci uninstall -h
      usage: nbcollection-ci uninstall [-h] [-t CI_TYPE] -r REPO_PATH
      
      Uninstall Astropy Jupyter notebook build machinery into a Source-Code Repository
      
      optional arguments:
        -h, --help            show this help message and exit
        -t CI_TYPE, --ci-type CI_TYPE
                              Supported CI-Types: [{', '.join([v.value for key, v in CIType.__members__.items()]}]
        -r REPO_PATH, --repo-path REPO_PATH
                              Local or remote path to repo to be uninstalled
      
      Example Usage:
      
          Uninstall machinery locally:
          nbcollection-ci uninstall --ci-type circle-ci --repo-path /tmp/my-new-repository
      
          Uninstall machinery remotely:
          nbcollection-ci uninstall --ci-type circle-ci --repo-path https://github.com/jbcurtin/notebooks


Virutal ENV Management
++++++++++++++++++++++

`nbcollection-ci venv` was created to create sample notebook environment for rapid testing

`nbcollection-ci venv` command is a tiny wrapper around managing differet virtual environment types. It provides a common
CLI API to manage your Notebook Environment, geared towards improving communication between team members. Often, for
scientists to collaborate its important to have the same tools installed. The learning curve for getting up and running
with Conda, VirtualENV, Python VENV, and Miniconda are all about the some, but its four different curves to learn

Instead, nbcollection ships with the most basic and easily repeatable steps for mananging the environment. Keep in mind,
we won't support you if something fails. We recommend you hire an infrastructure engineer to manage deployments

.. code-block:: bash

    $ pip install nbcollection -U
    $ nbcollection-ci venv -h
      usage: nbcollection venv [-h] [-e ENV_TYPE] [-d DIRECTORY] [-o]
      
      Wrapper around common virtual environment utils
      
      optional arguments:
        -h, --help            show this help message and exit
        -e ENV_TYPE, --env-type ENV_TYPE
                              ENVTypes Available: [python-venv, virtualenv, conda, mini-conda, smpc]
        -d DIRECTORY, --directory DIRECTORY
                              Which directory would you like to install
        -o, --overwrite       Overwrite ENV files?
      
      Example Usage:
      
          Create virtualenv:
          nbcollection-ci install --env-type venv -d /tmp/new-notebook


Launching Jupyter Lab
=====================

.. code-block:: bash

    $ pip install nbcollection -U
    $ nbcollection-ci venv -t virtual-env /tmp/new-notebook
    $ cd /tmp/new-notebook
    $ source venv/bin/activate
    $ jupyter-lab


Replicate
+++++++++

.. code-block:: bash

    $ pip install nbcollection -U
    $ nbcollection-ci replicate -h
      usage: nbcollection-ci replicate [-h] -t SOURCE
      
      Replicate Notebook Environments locally
      
      optional arguments:
        -h, --help            show this help message and exit
        -t SOURCE, --source SOURCE
                              See Example Usage
      
      Example Usage:
      
          Replicate Github PR locally:
          nbcollection-ci replicate --source https://github.com/spacetelescope/dat_pyinthesky/pull/111



See Also
--------

.. toctree::
    :maxdepth: 2

    # exceptions.rst
    # venv.rst

