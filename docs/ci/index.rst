nbcollection-ci Overview
########################

`nbcollection-ci` provides a collection of commands to manage Jupyter Notebook build machinery. It aims to monitor and
manage repositories at scale so the build engineer may provide a seamless experience for the Scientific Reviewers


License
-------

BSD 3-clause

Getting Started
---------------

Follow this `walkthrough <ci_example.html>`_ for an indepth guide into using `nbcollection-ci`


Folder Structure
++++++++++++++++

`nbcollection-ci` interprets all folders in the root level of the repository to be a collection. Each subsequent
folder is determined to be a Namespace or a Category. What makes a folder into a Category is, it contains `.ipynb` and
other files required for building notebooks. Such as a `requirements.txt` or `pre-install.sh`.

.. code-block:: text

    notebook_repo ( Repository )
    ├── notebook_collection_one
        └── first_level
            └── second_level
                └── notebook_category
                    ├── requirements.txt
                    ├── pre-install.sh
                    └── notebook.ipynb
    └── notebook_collection_two
        └── notebook_category
            ├── requirements.txt
            ├── pre-install.sh
            └── notebook.ipynb


Build Notebooks
+++++++++++++++

nbcollection-ci build-notebooks is the main entry point for rendering notebooks into different formats. When this process is ran, we can
extract information from notebooks using the metadata module such as Title and Description. Render that into other files for generation of indexes
and SEO html-elements. The notebook is also rendered into HTML/CSS using nbconvert

.. code-block:: bash

    $ pip install nbcollection -U
    $ nbcollection-ci build-notebooks --collection-names jdat_notebooks --category-names asdf_example --project-path /tmp/notebook-repository


Metadata
++++++++

Extracts information from a Category of notebooks and produces individualized json files with extracted information from notebooks. The CLI
aligns with Build Notebooks and there is a Pythonic interface that goes along with it.


.. code-block:: bash

    $ pip install nbcollection -U
    $ nbcollection-ci build-notebooks --collection-names jdat_notebooks --category-names asdf_example --project-path /tmp/notebook-repository


See Also
--------

.. toctree::
    :maxdepth: 2

    architecture.rst
    ci_example.rst
    ci_enable.rst
