nbcollection-ci
###############

nbcollection CI provides a tool to install CircleCI workflow files into you repository,


Install CI Integration
----------------------

.. code-block:: python

    $ pip install nbcollection -U
    $ nbcollection-ci install -t circle-ci -r https://github.com/adrn/nbcollection


Uninstall CI Integration
------------------------

.. code-block:: python

    $ pip install nbcollection -U
    $ nbcollection-ci uninstall -t circle-ci -r https://github.com/adrn/nbcollection


Create Virtual Environment
--------------------------

`nbcollection-ci venv` was created to create sample notebook environment for rapid testing

`nbcollection-ci venv` command is a tiny wrapper around managing differet virtual environment types. It provides a common
CLI API to manage your Notebook Environment, geared towards improving communication between team members. Often, for
scientists to collaborate its important to have the same tools installed. The learning curve for getting up and running
with Conda, VirtualENV, Python VENV, and Miniconda are all about the some, but its four different curves to learn

Instead, nbcollection ships with the most basic and easily repeatable steps for mananging the environment. Keep in mind,
we won't support you if something fails. We recommend you hire an infrastructure engineer to manage deployments


Install and Launch jupyter-lab
******************************

.. code-block:: bash

    $ pip install nbcollection -U
    $ nbcollection-ci venv -t virtual-env /tmp/new-notebook
    $ cd /tmp/new-notebook
    $ source venv/bin/activate
    $ jupyter-lab


See Also
--------

.. toctree::
    :maxdepth: 2

    exceptions.rst
    venv.rst

