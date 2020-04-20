nbcollection-ci venv
####################


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
    $ pip install nbcollection -U
    $ nbcollection-ci venv -t virtual-env /tmp/new-notebook
    $ cd /tmp/new-notebook
    $ source venv/bin/activate
    $ jupyter-lab


VENV Types
----------


Python venv
***********

( Not Implemented Yet )


virtualenv
**********

When `-o virtualenv` is passed into `nbcollection-ci venv`, a `virtualenv` is created relative to the directory
specified. `build.sh`, `requirements.txt`, and `.gitignore` are installed along with `venv` in that directory. Theres
are essential files laid out for the `nbcollection-ci` Pipeline. More details can be found here_

.. _here: https://github.com/adrn/nbcollection/issues/1#issuecomment-614665793

Example
=======

.. code-block:: bash

    nbcollection-ci venv -t virtualenv -d /tmp/new-notebook


Conda
*****

( Not Implemented Yet )


Mini Conda
**********

( Not Implemented Yet )

