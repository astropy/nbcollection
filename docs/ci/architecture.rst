# nbcollection-ci

`nbcollection-ci` is a suite of CLI tools designed to simplify maintaining, converting, and testing collections 
of Jupyter notebooks. The goal is to empower communities using GitHub, CircleCI, Jenkins and similar CI 
tools, to assist with building and reviewing Jupyter notebooks.

## Documentation URL

https://nbcollection.readthedocs.io/en/latest/

## Feature Request List

### Isolated Build Environments

Isolated build environments allow for notebooks to be built and rendered sequentially, concurrently, or in a Github PR.

For Github PRs, the way nbcollection-ci detects changes in the repository is by checking out a clone into a temporary
directory. It scans Github for all commits associated with the Pull Request and builds a diff from those objects.
Collections and Categories are detected on the filesystem and then built sequentially or concurrently

### Replication

The Review process has many steps. Each notebook must be reviewed by atleast three members. To make replication across
all environments easier. We've implemented `nbcollection-ci replicate`. Users can than install software to run the
the notebook quickly without having to learn any additional tools outside of pip, nbcollection-ci and Jupyter Lab.


.. code-block:: bash

    $ pip install nbcollection
    $ nbcollection-ci replicate --repo-path https://github.com/spacetelescope/dat_pyinthesky/pull/111 --project-path /tmp/notebook-replication



Additional Documentation
------------------------


.. toctree::
    :maxdepth: 1
    ci_example.rst

