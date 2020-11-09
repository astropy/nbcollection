nbcollection-ci Exceptions
##########################

Explanations about exceptions that can arise from `nbcollection-ci`

NBCollectionCI_InstallException
-------------------------------

NBCollectionCI_InstallException raises when users attempt to overwrite an installation of `nbcollection` into
a local or remote repository. It prevents re-installation or overwriting an already functioning CI Pipeline

NBCollectionCI_InvalidRepoPath
------------------------------

InvalidRepoPath indicates that the `--repo-path` or `-r` value entered is not a supported. Supported formats are:

* git@github.com:jbcurtin/nbcollection.git
* https://github.com/astropy/nbcollection
* /tmp/local-repo-path
* https://github.com/astropy/nbcollection/pull/10


.. toctree::
    :maxdepth: 1
