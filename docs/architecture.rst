Architecture, Terminology & API Introductions
---------------------------------------------

At the heart of Notebook CI is astropy's `nbcollection` & `nbcollection-ci`. This document will focus on `nbcollection-ci`, 
introducing modules and concepts used in the development.

A custom testing framework has been built into `nbcollection` so tests can be ran with file-system objects objects found
on remote systems. For more details, please refere to the Testing Architecture documentation.


Software Support
################

Python Version Support

======== ======= ===========
Software Version Test Status
======== ======= ===========
Python   3.6
Python   3.7
Python   3.8
Python   3.9
======== ======= ===========


Operating System Support

============== ======= ===========
OS Name        Version Test Status
============== ======= ===========
Ubuntu LTS     20.04
RHEL           7
macOS          10.15
Windows Server 2019
============== ======= ===========


Terminology
###########


* Notebook Collection: A notebook collection is a collection of categories, or folders just relative to the root-level of a Repository.
* Notebook Category: A notebook category is a folder of notebooks relative or deeply nested inside a notebook collection. There can be many categories per collection. Notebook Categories are transformed into isolated build environments and notebooks within are ordered and executed sequentially.
* Notebooks


CI/CD Checks and Utilities
##########################


* Bandit Security Audit
* Flake8 PEP-8
* Sphinx Link Checking
* Code Cov ( not yet configured )


Modules and Concepts
####################

Great care was taken to make the code maintainable. A majority of the code was written around the Scanner Module. You'll
find small implementations of the scanner module functions implemented throughout the codebase takes on most
complexe operations within `nbcollection-ci`.

At the core of the scanner module is the concept "Isolated Build Environments". This allows for a lot of encapsulation
and abstraction in various areas of the codebase. Including a Testing Architecture completely decoupled from
dependencies and commands, decoupled from the scanner module. The only hard dependencies on each module are objects
being passed through to the functions being ran. Making upgrading straightforward.

Let's dig into the APIs available

Scanner Module API
******************

Enumerating the Python API into bash was pretty straight forward. The only caveat to worry about is how to manage
multiple entries at once. In the Bash API, a comma seperated list can be passed into each option such as
`--collection-names`, `--category-names`, and `--notebook-names`.


Command Line API

.. code-block:: bash

    $ nbcollection-ci build-notebooks --collection-names jdat_notebooks,notebooks --project-path /tmp/dat_pyinthesky


Python API

.. code-block:: python

    from nbcollection.ci.scanner.utils import find_build_jobs, generate_job_context, run_job_context
    
    project_path = '/tmp/dat_pyinthesky'
    collection_names = ['jdat_notebooks', 'notebooks']
    
    for job_idx, job in enumerate(find_build_jobs(project_path, collection_names)):
    
        # Construct an isolated build environment by generating the job context
        job_context = generate_job_context(job)
    
        # Execute Jupyter Notebooks by running the Job Context
        run_job_context(job_context)


Metadata Module API
*******************

`nbcollection.ci.metadata` implements functions to extract useful information from Jupyter Notebooks.

The logic inspects each Jupyter Notebook for `title` and `description` and provides a python datatype.


Extracting Metadata
+++++++++++++++++++

Command Line API

.. code-block:: bash

    nbcollection-ci metadata --mode extract-metadata --collection-names jdat_notebooks --project-path /tmp/dat_pyinthesky --category-name asdf_example


Python API

.. code-block:: python

    # Extract Metadata from 
    from nbcollection.ci.scanner.utils import find_build_jobs, generate_job_context
    from nbcollection.ci.metadata.utils import extract_metadata
    
    project_path = '/tmp/dat_pyinthesky'
    collection_names = ['jdat_notebooks']
    category_names = ['asdf_example']
    
    for job in find_build_job(project_path, collection_names, category_names):
        job_context = generate_job_context(job)
        for notebook_context in job_context.notebooks:
            metadata = extract_metadata(notebook_context)


Reset Notebooks
+++++++++++++++

Resets Jupyter Notebook cell output.

Command Line API

.. code-block:: bash

    nbcollection-ci metadata --mode reset-notebooks --collection-names jdat_notebooks --project-path /tmp/dat_pyinthesky --category-name asdf_example

Python API

.. code-block:: python

    import json
    
    from nbcollection.ci.scanner.utils import find_build_jobs, generate_job_context
    from nbcollection.ci.metadata.utils import reset_notebook_execution
    
    project_path = '/tmp/dat_pyinthesky'
    collection_names = ['jdat_notebooks']
    category_names = ['asdf_example']
    
    for job in find_build_job(project_path, collection_names, category_names):
        job_context = generate_job_context(job)
        for notebook_context in job_context.notebooks:
            with open(notebook_context.path, 'rb') as stream:
                notebook_data = json.loads(stream.read().decode(ENCODING))
    
            reset_notebook_execution(notebook_data)
    
            with open(notebook_context.path, 'wb') as stream:
                stream.write(json.dumps(notebook_data).encode(ENCODING))


Generate CI Environment
***********************

`nbcollection-ci generate-ci-env` accepts an arbitrary number of Collection, Category, and Notebooks. Takes the
information and renders into a configuration file of which can be submitted to a CI/CD pipeline. The logic is
flexible enough to generate configs for CircleCI, Github Actions, AWS CloudFormation for Lambda, or K8 Yaml files if
need be.

Command Line API

.. code-block:: bash

    $ nbcollection-ci generate-ci-env --collection-names jdat_notebooks --ci-environment circle-ci --project-path /tmp/dat_pyinthesky

Python API

.. code-block:: python

    from nbcollection.ci.commands.datatypes import CIEnvironment
    from nbcollection.ci.generate_ci_environment.utils import gen_ci_env
    
    project_path = '/tmp/dat_pyinthesky'
    collection_names = ['jdat_notebooks']
    jobs = []
    
    for job in find_build_jobs(project_path, collection_names):
        jobs.append(job)
    
    gen_ci_env(jobs, CIEnvironment.CircleCI, project_path)


Merge Artifacts
***************

Artifacts are generated by previously ran commands and could be available in CircleCI or locally in a temporary folder.
To merge these artifacts into a single website, which is generated from a theme from within nbcollection.ci, this
`merge-artifacts` command will need a CIRCLECI_TOKEN to run successfully.

The logic of this command identifies which notebooks have been built recently in CircleCI. Downloads and
stores the Notebooks with other artifacts in a temporary folder. A website is then generated from the downloaded
artifacts using a Beautiful Soup lxml parser. Extracts the core HTML from the built Jupyter Notebook and renders into
a Jinja2 Website Theme.

Command Line API

.. code-block:: bash

    $ nbcollection-ci merge-artifacts --org spacetelescope --repo-name dat_pyinthesky

Python API

.. code-block:: python

    from nbcollection.ci.merge_artifacts.utils import artifact_merge
    
    project_path = '/tmp/dat_pyinthesky'
    repo_name = 'dat_pyinthesky'
    org = 'spacetelescope'
    collection_names = ['jdat_notebooks']
    
    artifact_merge(project_path, repo_name, org, collection_names)

Build Notebooks
***************

`nbcollection-ci build-notebooks` is where most of the work is done. The scope of the command can take in entire collections,
categories, or notebooks. Narrowing down the scope of the notebook builds allows for concurrent builds to be ran through
the command line interface for CI/CD to accuratly report failures in services such as CircleCI or Github Actions.

The logic of the command accepts an arbitrary set of Notebook Collections, Categories, and/or Notebooks. Of which will
than be sequentially executed in alphabetical order.

Command Line API

.. code-block:: bash

    nbcollection-ci build-notebooks --collection-names jdat_notebooks --category-names asdf_example


Alternatively, there are also utility options for the power user which will run all the notebook builds in different
processes with a single command.

The logic of the command accepts an arbitrary set of Notebook Collections, Category, and/or Notebooks. Of which are
than piped into concurrent processes where each process executes a single category on notebooks. If the category takes
advantage of multiple cores on the machine, `build-notebook` isn't written to measure available resources. Its up to
the notebooks to know if the CPUs are busy. All memory managment is assumed, managed by a Python Interpreter or
Operating System.


Command Line API

.. code-block:: bash

    nbcollection-ci build-notebooks --collection-names jdat_notebooks -b concurrent -w 4

Either way `nbcollection-ci build-notebooks` is ran, artifacts will be saved in `/tmp/nbcollection-ci-artifacts`.


Pull Request
************

`nbcollection-ci pull-request` is only used inside a pull request. Chances are the only reason to run locally will be
to debug code or problematic behaviour of the program.

The logic of the command accepts an URI as input in the command line. Followed by parsing the URI into a nbcollection
datatype called RepoType. Checks to see if the URI passed is a Github Pull Request. Then parse the URI,
extracting all the meta-data associated with a Github Pull Request. Next making a call to the Github Pull Request API,
learning more about the Pull Request to be tested. It then checks to see which files have been explicitly added within
the Github Pull Request, and builds notebooks accordingly.

Command Line API

.. code-block:: bash

    nbcollection-ci pull-request -u https://github.com/spacetelescope/dat_pyinthesky/pull/139


Site Deployment
***************

`nbcollection-ci site-deployment` takes care of publishing a in Github Pages. Should be installed into the build
machinery of the repository with the -w command from `nbcorrection-ci generate-ci-env`

The logic of the command, starts by checking to see if a Pull Request was created. If yes, stop running because
overriding a published website with a Pull Request would lead to an inconsistent User Experience. Through python, the
command inspects the `.git/config` file using GitPython. Checking for a remote which to push to. Then makes a
copy of the `site/` directory, pushing the published website into a Github Branch.


Command Line API

.. code-block:: bash

    nbcollection-ci site-deployment -r origin -b gh-pages


Sync Notebooks
**************

`nbcollection-ci sync-notebooks` provides an automated action to sync notebooks from one repository to the next. Taking
in a set of collection and/or categories and copying the notebooks within to a destination folder.

.. code-block:: bash

    # Copy all notebooks within spacetelescope/dat_pyinthesky/jdat_notebooks to spacetelescope/jdat_notebooks/notebooks
    nbcollection-ci sync-notebooks -c jdat_notebooks -d ../jdat_notebooks/notebooks
