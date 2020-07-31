nbcollection ci
###############

CLI
---

.. code-block:: bash

    PYTHONPATH='.' python -m nbcollection.ci venv -e virtualenv -d /tmp/new-notebook -o


pytest
------

.. code-block:: bash

    pytest nbcollection_tests/ci/test_generator.py::test__CircleCiRepo__install 

