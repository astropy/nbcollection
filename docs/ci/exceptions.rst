nbcollection-ci Exceptions
##########################

Explanations about exceptions that can arise from `nbcollection-ci`

NBCollectionCI_InstallException
-------------------------------

To provent users from overwriting files in repositories, `--overwrite` or `-o` must be passed when running
`nbcollection-ci install`

Example Usage
*************

.. code-block:: bash

    $ nbcollection-ci install -t circle-ci -r git@github.com:jbcurtin/nbcollection.git -o


NBCollectionCI_InvalidRepoPath
------------------------------

InvalidRepoPath indicates that the `--repo-path` or `-r` value entered is not a supported. Supported formats are

* git@github.com:jbcurtin/nbcollection.git
* https://github.com/jbcurtin/nbcollection
* /tmp/local-repo-path


Example Usage
*************

.. code-block:: bash

    $ nbcollection-ci install -t circle-ci -r git@github.com:jbcurtin/nbcollection.git
    $ nbcollection-ci uninstall -t circle-ci -r git@github.com:jbcurtin/nbcollection.git

