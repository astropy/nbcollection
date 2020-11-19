Enable nbcollection-ci in a repository
--------------------------------------

`nbcollection-ci` is designed to be installed locally with python-pip or git. It provides a set of commands that will
install and assist in managing CI/CD Pipelines. Only CirclCI is supported, however it's still straight forward to add
nbcollection-ci to Github Actions, Jenkins or another CI/CD solution.

This document covers what it takes to enable `nbcollection-ci` in a new repository. Starting with the expected folder
structure, installation of `nbcollection-ci`_, generating a `config.yml`_ file, and showing how to check CircleCI to make
sure the build machinery was installed correctly.

.. _`nbcollection-ci`: https://github.com/astropy/nbcollection
.. _`config.yml`: https://circleci.com/docs/2.0/sample-config/


Expected Folder Structure of a Repository
=========================================

Here is a birds eye view of the expected folder structure. For a details understanding of what a Collection or Category is, 
please refer to `ci_example <ci_example.html#>`_. For the purposes for this document. We'll assume the a folder structure
simular to below has already been implemented.

.. code-block:: text

    spacetelescope/notebooks
    ├── collection_one
    └── jdat_notebooks
        └── asdf_example
            ├── asdf_example.ipynb
            ├── pre-install.sh
            ├── pre-requirements.txt
            └── requirements.txt


Installing nbcollection-ci
==========================

`nbcollection-ci` can be installed via git + python. Clone `astropy/nbcollection` and run `python setup.py`


.. code-block:: bash

    $ git clone https://github.com/jbcurtin/nbcollection $HOME/nbcollection
    $ cd $HOME/nbcollection
    $ pip install -r ci_requirements.txt
    $ python setup.py install


If you'd like to delay installing `nbcollection-ci` locally, a docker container available to try out `nbcollection-ci`

.. code-block:: bash

    $ docker run -it --rm jbcurtin/nbcollection-bulider /bin/bash


Enabling nbcollection-ci Build Machinery
========================================

With `nbcollection-ci` installed and a compatable folder structure created in `spacetelescope/notebooks`. Install Build 
Machinery with the following steps


.. code-block:: bash

    $ git clone git@github.com:spacetelescope/notebooks /tmp/notebooks
    $ nbcollection-ci generate-ci-env --project-path /tmp/notebooks --collection-names notebooks
    $ cd /tmp/notebooks
    $ git remote rename origin spacetelescope
    $ git commit -m 'Added CircleCI Build Machinery with nbcollection-ci' -a
    $ git push spacetelescope main


Add a CircleCI Project
======================

For the last step of this process, authenticate your Github Account and add a project via CircleCI.
https://circleci.com/docs/2.0/project-build/#adding-projects

